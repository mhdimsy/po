from __future__ import annotations

from dataclasses import dataclass

from sqlmodel import Session, select

from app.core.time import utc_now
from app.modules.events.models import (
    CurrentInventoryState,
    CurrentMachineState,
    CurrentOperationState,
    CurrentOperatorState,
)
from app.modules.events.schemas import EventAppendRequest
from app.modules.events.service import append_event
from app.modules.optimizer.models import OptimizationRun, ScheduleOperation
from app.modules.optimizer.schemas import AcceptScheduleResponse, OptimizerRunRequest, OptimizerRunResponse
from app.modules.scenarios.models import Scenario


SCHEDULABLE_OPERATION_STATUSES = {
    "Queued",
    "WaitingMaterial",
    "WaitingMachine",
    "WaitingOperator",
    "Setup",
}


@dataclass
class ResourcePool:
    machine_ids: list[str]
    operator_ids: list[str]
    machine_available_at: dict[str, int]
    operator_available_at: dict[str, int]


def run_optimizer(session: Session, request: OptimizerRunRequest) -> OptimizerRunResponse:
    ensure_scenario_exists(session, request.scenario_id)
    operations = get_schedulable_operations(session, request.scenario_id)
    resource_pool = build_resource_pool(session, request.scenario_id)

    run = OptimizationRun(
        scenario_id=request.scenario_id,
        trigger_type=request.trigger_type,
        policy_json=request.policy_json,
        risk_mode=request.risk_mode,
        frozen_window_minutes=request.frozen_window_minutes,
        status="Suggested",
    )
    session.add(run)
    session.flush()

    schedule_rows: list[ScheduleOperation] = []
    current_time = request.frozen_window_minutes
    previous_operation_end_by_order: dict[str, int] = {}

    for operation in sorted(operations, key=operation_sort_key):
        payload = operation.payload_json or {}
        duration = max(1, int(payload.get("operation_duration") or payload.get("duration") or 60))
        order_id = operation.order_id or string_or_none(payload.get("order_id"))
        machine_id = choose_machine(operation, resource_pool, payload)
        operator_id = choose_operator(operation, resource_pool, payload)

        earliest_start = max(current_time, operation.simulation_time or 0)
        if order_id is not None:
            earliest_start = max(earliest_start, previous_operation_end_by_order.get(order_id, 0))
        if machine_id is not None:
            earliest_start = max(earliest_start, resource_pool.machine_available_at.get(machine_id, 0))
        if operator_id is not None:
            earliest_start = max(earliest_start, resource_pool.operator_available_at.get(operator_id, 0))

        blocked_reason = material_block_reason(session, request.scenario_id, payload)
        status = "Suggested" if blocked_reason is None else "Blocked"
        if blocked_reason is not None:
            start_time = earliest_start
            end_time = earliest_start
            score = 0
        else:
            start_time = earliest_start
            end_time = start_time + duration
            score = score_operation(payload, start_time, end_time)
            if machine_id is not None:
                resource_pool.machine_available_at[machine_id] = end_time
            if operator_id is not None:
                resource_pool.operator_available_at[operator_id] = end_time
            if order_id is not None:
                previous_operation_end_by_order[order_id] = end_time

        changed = has_schedule_changed(payload, machine_id, operator_id, start_time, end_time)
        schedule = ScheduleOperation(
            optimization_run_id=run.id,
            operation_id=operation.operation_id,
            order_id=order_id,
            machine_id=machine_id,
            operator_id=operator_id,
            start_time=start_time,
            end_time=end_time,
            status=status,
            score=score,
            reason_json={
                "source_status": operation.status,
                "duration": duration,
                "priority": payload.get("priority", payload.get("priority_score")),
                "due_time": payload.get("due_time"),
                "changed": changed,
                "blocked_reason": blocked_reason,
                "constraints_checked": [
                    "precedence_by_order_sequence",
                    "machine_availability",
                    "operator_availability",
                    "material_availability",
                    "frozen_window",
                    "order_priority",
                    "due_time",
                ],
            },
        )
        session.add(schedule)
        session.flush()
        schedule_rows.append(schedule)

    changed_count = sum(1 for item in schedule_rows if item.reason_json.get("changed"))
    run.changed_operations_count = changed_count
    run.score = calculate_run_score(schedule_rows)
    session.add(run)
    session.flush()

    append_event(
        session,
        EventAppendRequest(
            event_type="ScheduleSuggested",
            aggregate_type="OptimizationRun",
            aggregate_id=str(run.id),
            scenario_id=request.scenario_id,
            payload_json={
                "optimization_run_id": run.id,
                "score": run.score,
                "changed_operations_count": changed_count,
                "operation_count": len(schedule_rows),
            },
            update_current_state=False,
        ),
    )
    session.refresh(run)
    for row in schedule_rows:
        session.refresh(row)
    return OptimizerRunResponse(run=run, schedule=schedule_rows)


def accept_schedule(session: Session, optimization_run_id: int) -> AcceptScheduleResponse:
    run = session.get(OptimizationRun, optimization_run_id)
    if run is None:
        raise RuntimeError(f"OptimizationRun {optimization_run_id} was not found.")
    if run.status == "Accepted":
        schedule_rows = list_schedule(session, optimization_run_id)
        return AcceptScheduleResponse(run=run, accepted_operations=len(schedule_rows))

    schedule_rows = list_schedule(session, optimization_run_id)
    run.status = "Accepted"
    run.accepted_at = utc_now()
    session.add(run)

    accepted_count = 0
    for schedule in schedule_rows:
        schedule.status = "Accepted"
        session.add(schedule)
        accepted_count += 1
        append_event(
            session,
            EventAppendRequest(
                event_type="OperationScheduled",
                aggregate_type="Operation",
                aggregate_id=schedule.operation_id,
                scenario_id=run.scenario_id,
                simulation_time=schedule.start_time,
                payload_json={
                    "status": "Queued",
                    "order_id": schedule.order_id,
                    "machine_id": schedule.machine_id,
                    "operator_id": schedule.operator_id,
                    "scheduled_start": schedule.start_time,
                    "scheduled_end": schedule.end_time,
                    "optimization_run_id": run.id,
                },
            ),
        )

    append_event(
        session,
        EventAppendRequest(
            event_type="ScheduleAccepted",
            aggregate_type="OptimizationRun",
            aggregate_id=str(run.id),
            scenario_id=run.scenario_id,
            payload_json={
                "optimization_run_id": run.id,
                "accepted_operations": accepted_count,
                "score": run.score,
            },
            update_current_state=False,
        ),
    )
    session.refresh(run)
    return AcceptScheduleResponse(run=run, accepted_operations=accepted_count)


def list_optimizer_runs(session: Session, scenario_id: int | None = None) -> list[OptimizationRun]:
    statement = select(OptimizationRun).order_by(OptimizationRun.id.desc())
    if scenario_id is not None:
        statement = statement.where(OptimizationRun.scenario_id == scenario_id)
    return list(session.exec(statement).all())


def list_schedule(session: Session, optimization_run_id: int) -> list[ScheduleOperation]:
    return list(
        session.exec(
            select(ScheduleOperation)
            .where(ScheduleOperation.optimization_run_id == optimization_run_id)
            .order_by(ScheduleOperation.start_time, ScheduleOperation.id)
        ).all()
    )


def get_schedulable_operations(session: Session, scenario_id: int) -> list[CurrentOperationState]:
    return list(
        session.exec(
            select(CurrentOperationState)
            .where(CurrentOperationState.scenario_id == scenario_id)
            .where(CurrentOperationState.status.in_(SCHEDULABLE_OPERATION_STATUSES))
        ).all()
    )


def build_resource_pool(session: Session, scenario_id: int) -> ResourcePool:
    machines = session.exec(select(CurrentMachineState).where(CurrentMachineState.scenario_id == scenario_id)).all()
    operators = session.exec(select(CurrentOperatorState).where(CurrentOperatorState.scenario_id == scenario_id)).all()
    machine_ids = [machine.machine_id for machine in machines if machine.status in {"Available", "Idle", "Reserved"}]
    operator_ids = [operator.operator_id for operator in operators if operator.status in {"Available", "Reserved"}]
    return ResourcePool(
        machine_ids=machine_ids,
        operator_ids=operator_ids,
        machine_available_at={machine_id: 0 for machine_id in machine_ids},
        operator_available_at={operator_id: 0 for operator_id in operator_ids},
    )


def choose_machine(operation: CurrentOperationState, pool: ResourcePool, payload: dict) -> str | None:
    requested = string_or_none(payload.get("machine_id") or operation.machine_id)
    if requested in pool.machine_ids:
        return requested
    if not pool.machine_ids:
        return requested
    return min(pool.machine_ids, key=lambda machine_id: pool.machine_available_at.get(machine_id, 0))


def choose_operator(operation: CurrentOperationState, pool: ResourcePool, payload: dict) -> str | None:
    requested = string_or_none(payload.get("operator_id") or operation.operator_id)
    if requested in pool.operator_ids:
        return requested
    if not pool.operator_ids:
        return requested
    return min(pool.operator_ids, key=lambda operator_id: pool.operator_available_at.get(operator_id, 0))


def material_block_reason(session: Session, scenario_id: int, payload: dict) -> str | None:
    required_inventory_id = string_or_none(payload.get("required_inventory_item_id"))
    required_qty = float(payload.get("required_qty") or 0)
    if required_inventory_id is None or required_qty <= 0:
        return None
    inventory = session.exec(
        select(CurrentInventoryState)
        .where(CurrentInventoryState.scenario_id == scenario_id)
        .where(CurrentInventoryState.inventory_item_id == required_inventory_id)
    ).first()
    if inventory is None:
        return "required_inventory_missing"
    available_qty = inventory.on_hand_qty - inventory.reserved_qty
    if available_qty < required_qty:
        return "material_unavailable"
    return None


def operation_sort_key(operation: CurrentOperationState):
    payload = operation.payload_json or {}
    priority = float(payload.get("priority") or payload.get("priority_score") or 0)
    due_time = int(payload.get("due_time") or 1_000_000_000)
    sequence = int(payload.get("operation_sequence") or 1_000_000)
    return (-priority, due_time, sequence, operation.id or 0)


def has_schedule_changed(payload: dict, machine_id: str | None, operator_id: str | None, start_time: int, end_time: int) -> bool:
    return any(
        [
            string_or_none(payload.get("machine_id")) != machine_id if payload.get("machine_id") is not None else False,
            string_or_none(payload.get("operator_id")) != operator_id if payload.get("operator_id") is not None else False,
            payload.get("scheduled_start") != start_time,
            payload.get("scheduled_end") != end_time,
        ]
    )


def score_operation(payload: dict, start_time: int, end_time: int) -> float:
    due_time = payload.get("due_time")
    priority = float(payload.get("priority") or payload.get("priority_score") or 1)
    delay = max(0, end_time - int(due_time)) if due_time is not None else 0
    return max(0, 100 + priority * 10 - delay)


def calculate_run_score(schedule_rows: list[ScheduleOperation]) -> float:
    if not schedule_rows:
        return 0
    return round(sum(item.score for item in schedule_rows) / len(schedule_rows), 2)


def string_or_none(value) -> str | None:
    if value is None:
        return None
    return str(value)


def ensure_scenario_exists(session: Session, scenario_id: int) -> None:
    if session.get(Scenario, scenario_id) is None:
        raise RuntimeError(f"Scenario {scenario_id} was not found.")
