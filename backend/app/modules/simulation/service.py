from __future__ import annotations

from sqlalchemy import case
from sqlmodel import Session, select

from app.core.time import utc_now
from app.modules.events.models import CurrentMachineState, CurrentOperationState
from app.modules.events.schemas import EventAppendRequest
from app.modules.events.service import append_event
from app.modules.scenarios.models import Scenario
from app.modules.simulation.models import SimulationRun
from app.modules.simulation.schemas import SimulationStartRequest, SimulationStepRequest, SimulationStepResponse


OPERATION_TRANSITIONS = {
    "Queued": ("OperationSetup", "Setup"),
    "WaitingMaterial": ("OperationBlocked", "Blocked"),
    "WaitingMachine": ("OperationBlocked", "Blocked"),
    "WaitingOperator": ("OperationBlocked", "Blocked"),
    "Setup": ("OperationStarted", "Running"),
    "Running": ("OperationFinished", "Finished"),
}


def start_simulation(session: Session, scenario_id: int, request: SimulationStartRequest) -> SimulationRun:
    ensure_scenario_exists(session, scenario_id)
    existing_run = get_active_run(session, scenario_id)
    if existing_run is not None:
        return existing_run

    run = SimulationRun(
        scenario_id=scenario_id,
        status="Running",
        speed_factor=request.speed_factor,
        current_sim_time=request.start_time,
    )
    session.add(run)
    session.flush()
    append_event(
        session,
        EventAppendRequest(
            event_type="SimulationStarted",
            aggregate_type="SimulationRun",
            aggregate_id=str(run.id),
            scenario_id=scenario_id,
            simulation_time=run.current_sim_time,
            payload_json={
                "simulation_run_id": run.id,
                "speed_factor": run.speed_factor,
                "status": run.status,
            },
            update_current_state=False,
        ),
    )
    session.refresh(run)
    return run


def pause_simulation(session: Session, scenario_id: int) -> SimulationRun:
    run = require_active_or_paused_run(session, scenario_id)
    run.status = "Paused"
    run.paused_at = utc_now()
    session.add(run)
    session.flush()
    append_event(
        session,
        EventAppendRequest(
            event_type="SimulationPaused",
            aggregate_type="SimulationRun",
            aggregate_id=str(run.id),
            scenario_id=scenario_id,
            simulation_time=run.current_sim_time,
            payload_json={"simulation_run_id": run.id, "status": run.status},
            update_current_state=False,
        ),
    )
    session.refresh(run)
    return run


def resume_simulation(session: Session, scenario_id: int) -> SimulationRun:
    run = require_active_or_paused_run(session, scenario_id)
    run.status = "Running"
    run.paused_at = None
    session.add(run)
    session.flush()
    append_event(
        session,
        EventAppendRequest(
            event_type="SimulationResumed",
            aggregate_type="SimulationRun",
            aggregate_id=str(run.id),
            scenario_id=scenario_id,
            simulation_time=run.current_sim_time,
            payload_json={"simulation_run_id": run.id, "status": run.status},
            update_current_state=False,
        ),
    )
    session.refresh(run)
    return run


def step_simulation(session: Session, scenario_id: int, request: SimulationStepRequest) -> SimulationStepResponse:
    run = require_active_or_paused_run(session, scenario_id)
    run.current_sim_time += request.minutes
    session.add(run)
    session.flush()
    append_event(
        session,
        EventAppendRequest(
            event_type="SimulationStepped",
            aggregate_type="SimulationRun",
            aggregate_id=str(run.id),
            scenario_id=scenario_id,
            simulation_time=run.current_sim_time,
            payload_json={
                "simulation_run_id": run.id,
                "minutes": request.minutes,
                "current_sim_time": run.current_sim_time,
            },
            update_current_state=False,
        ),
    )

    events_created = 1
    transitions: list[dict] = []
    if request.process_one_operation:
        transition_limit = request.max_operation_transitions or min(max(1, request.minutes), 120)
        transitions = transition_operations(session, scenario_id, run.current_sim_time, transition_limit)
        events_created += len(transitions)
        sync_machine_states_from_operations(session, scenario_id, run.current_sim_time)

    session.refresh(run)
    return SimulationStepResponse(
        run=run,
        events_created=events_created,
        operation_transition=transitions[-1] if transitions else None,
        operation_transitions=transitions,
    )


def transition_operations(session: Session, scenario_id: int, simulation_time: int, limit: int) -> list[dict]:
    transitions: list[dict] = []
    for _ in range(limit):
        transition = transition_one_operation(session, scenario_id, simulation_time)
        if transition is None:
            break
        transitions.append(transition)
    return transitions


def transition_one_operation(session: Session, scenario_id: int, simulation_time: int) -> dict | None:
    operation = session.exec(
        select(CurrentOperationState)
        .where(CurrentOperationState.scenario_id == scenario_id)
        .where(CurrentOperationState.status.in_(list(OPERATION_TRANSITIONS.keys())))
        .order_by(status_priority_case(), CurrentOperationState.id)
    ).first()
    if operation is None:
        return None

    previous_status = operation.status
    event_type, next_status = OPERATION_TRANSITIONS[previous_status]
    append_event(
        session,
        EventAppendRequest(
            event_type=event_type,
            aggregate_type="Operation",
            aggregate_id=operation.operation_id,
            scenario_id=scenario_id,
            simulation_time=simulation_time,
            payload_json={
                "status": next_status,
                "order_id": operation.order_id,
                "machine_id": operation.machine_id,
                "operator_id": operation.operator_id,
                "previous_status": previous_status,
            },
        ),
    )
    return {
        "operation_id": operation.operation_id,
        "machine_id": operation.machine_id,
        "operator_id": operation.operator_id,
        "previous_status": previous_status,
        "next_status": next_status,
        "event_type": event_type,
    }


def sync_machine_states_from_operations(session: Session, scenario_id: int, simulation_time: int) -> None:
    running_operations = session.exec(
        select(CurrentOperationState)
        .where(CurrentOperationState.scenario_id == scenario_id)
        .where(CurrentOperationState.status.in_(["Running", "Setup", "QC", "Rework"]))
    ).all()
    operation_by_machine = {
        operation.machine_id: operation
        for operation in running_operations
        if operation.machine_id is not None
    }
    machines = session.exec(select(CurrentMachineState).where(CurrentMachineState.scenario_id == scenario_id)).all()
    for machine in machines:
        running_operation = operation_by_machine.get(machine.machine_id)
        if running_operation is None:
            if machine.status in {"Busy", "Running", "Setup"}:
                machine.status = "Available"
                machine.current_operation_id = None
                machine.simulation_time = simulation_time
                session.add(machine)
            continue
        machine.status = "Running" if running_operation.status == "Running" else "Busy"
        machine.current_operation_id = running_operation.operation_id
        machine.simulation_time = simulation_time
        machine.payload_json = {
            **(machine.payload_json or {}),
            "current_operation_status": running_operation.status,
            "current_order_id": running_operation.order_id,
        }
        session.add(machine)
    session.commit()


def status_priority_case():
    return case(
        (CurrentOperationState.status == "Setup", 0),
        (CurrentOperationState.status == "Queued", 1),
        (CurrentOperationState.status == "Running", 2),
        else_=3,
    )


def list_simulation_runs(session: Session, scenario_id: int) -> list[SimulationRun]:
    return list(
        session.exec(
            select(SimulationRun)
            .where(SimulationRun.scenario_id == scenario_id)
            .order_by(SimulationRun.id.desc())
        ).all()
    )


def ensure_scenario_exists(session: Session, scenario_id: int) -> None:
    if session.get(Scenario, scenario_id) is None:
        raise RuntimeError(f"Scenario {scenario_id} was not found.")


def get_active_run(session: Session, scenario_id: int) -> SimulationRun | None:
    return session.exec(
        select(SimulationRun)
        .where(SimulationRun.scenario_id == scenario_id)
        .where(SimulationRun.status.in_(["Running", "Paused"]))
        .order_by(SimulationRun.id.desc())
    ).first()


def require_active_or_paused_run(session: Session, scenario_id: int) -> SimulationRun:
    ensure_scenario_exists(session, scenario_id)
    run = get_active_run(session, scenario_id)
    if run is None:
        raise RuntimeError(f"No active simulation run exists for scenario {scenario_id}.")
    return run
