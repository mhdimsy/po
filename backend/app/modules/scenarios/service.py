from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.modules.events.models import (
    CurrentInventoryState,
    CurrentMachineState,
    CurrentOperationState,
    CurrentOperatorState,
    CurrentOrderState,
)
from app.modules.events.schemas import EventAppendRequest
from app.modules.events.service import append_event
from app.modules.scenarios.models import Scenario, Snapshot
from app.modules.scenarios.schemas import (
    ScenarioCreateRequest,
    ScenarioForkRequest,
    SnapshotCreateRequest,
)


def create_scenario(session: Session, request: ScenarioCreateRequest) -> Scenario:
    scenario = Scenario(
        name=request.name,
        base_import_batch_id=request.base_import_batch_id,
        status=request.status,
        settings_json=request.settings_json,
        notes=request.notes,
    )
    session.add(scenario)
    session.flush()
    append_event(
        session,
        EventAppendRequest(
            event_type="ScenarioCreated",
            aggregate_type="Scenario",
            aggregate_id=str(scenario.id),
            scenario_id=scenario.id,
            payload_json={
                "name": scenario.name,
                "base_import_batch_id": scenario.base_import_batch_id,
                "status": scenario.status,
            },
            update_current_state=False,
        ),
    )
    session.refresh(scenario)
    return scenario


def fork_scenario(session: Session, source_scenario_id: int, request: ScenarioForkRequest) -> Scenario:
    source = session.get(Scenario, source_scenario_id)
    if source is None:
        raise RuntimeError(f"Scenario {source_scenario_id} was not found.")

    scenario = Scenario(
        name=request.name,
        base_import_batch_id=source.base_import_batch_id,
        parent_scenario_id=source.id,
        base_snapshot_id=request.base_snapshot_id,
        status="Draft",
        settings_json={**(source.settings_json or {}), **request.settings_json},
        notes=request.notes,
    )
    session.add(scenario)
    session.flush()
    append_event(
        session,
        EventAppendRequest(
            event_type="ScenarioForked",
            aggregate_type="Scenario",
            aggregate_id=str(scenario.id),
            scenario_id=scenario.id,
            payload_json={
                "parent_scenario_id": source.id,
                "base_snapshot_id": request.base_snapshot_id,
                "name": scenario.name,
            },
            update_current_state=False,
        ),
    )
    session.refresh(scenario)
    return scenario


def create_snapshot(session: Session, scenario_id: int, request: SnapshotCreateRequest) -> Snapshot:
    scenario = session.get(Scenario, scenario_id)
    if scenario is None:
        raise RuntimeError(f"Scenario {scenario_id} was not found.")

    state_json = collect_current_state(session, scenario_id)
    snapshot = Snapshot(
        scenario_id=scenario_id,
        snapshot_time=request.snapshot_time,
        reason=request.reason,
        metadata_json={
            **request.metadata_json,
            "scenario_name": scenario.name,
            "current_state_counts": {
                key: len(value)
                for key, value in state_json.items()
            },
        },
        state_json=state_json,
    )
    session.add(snapshot)
    session.flush()
    append_event(
        session,
        EventAppendRequest(
            event_type="SnapshotCreated",
            aggregate_type="Snapshot",
            aggregate_id=str(snapshot.id),
            scenario_id=scenario_id,
            payload_json={
                "snapshot_id": snapshot.id,
                "reason": snapshot.reason,
                "snapshot_time": snapshot.snapshot_time,
            },
            simulation_time=snapshot.snapshot_time,
            update_current_state=False,
        ),
    )
    session.refresh(snapshot)
    return snapshot


def collect_current_state(session: Session, scenario_id: int) -> dict[str, list[dict[str, Any]]]:
    return {
        "orders": dump_rows(session.exec(select(CurrentOrderState).where(CurrentOrderState.scenario_id == scenario_id)).all()),
        "operations": dump_rows(session.exec(select(CurrentOperationState).where(CurrentOperationState.scenario_id == scenario_id)).all()),
        "machines": dump_rows(session.exec(select(CurrentMachineState).where(CurrentMachineState.scenario_id == scenario_id)).all()),
        "operators": dump_rows(session.exec(select(CurrentOperatorState).where(CurrentOperatorState.scenario_id == scenario_id)).all()),
        "inventory": dump_rows(session.exec(select(CurrentInventoryState).where(CurrentInventoryState.scenario_id == scenario_id)).all()),
    }


def dump_rows(rows: list[Any]) -> list[dict[str, Any]]:
    return [json_safe(row.model_dump()) for row in rows]


def json_safe(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    return value
