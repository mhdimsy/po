from __future__ import annotations

from typing import Type

from sqlmodel import Session, SQLModel, select

from app.core.time import utc_now
from app.modules.events.models import (
    CurrentInventoryState,
    CurrentMachineState,
    CurrentOperationState,
    CurrentOperatorState,
    CurrentOrderState,
    EventStore,
)
from app.modules.events.schemas import EventAppendRequest, EventAppendResponse


def append_event(session: Session, request: EventAppendRequest) -> EventAppendResponse:
    event = EventStore(
        event_type=request.event_type,
        aggregate_type=request.aggregate_type,
        aggregate_id=request.aggregate_id,
        scenario_id=request.scenario_id,
        payload_json=request.payload_json,
        simulation_time=request.simulation_time,
    )
    session.add(event)
    session.flush()

    current_state_updated = False
    if request.update_current_state:
        current_state_updated = apply_current_state_projection(session, event)

    session.commit()
    session.refresh(event)
    return EventAppendResponse(event=event, current_state_updated=current_state_updated)


def apply_current_state_projection(session: Session, event: EventStore) -> bool:
    aggregate_type = event.aggregate_type.lower()
    if aggregate_type in {"order", "productionorder"}:
        upsert_order_state(session, event)
        return True
    if aggregate_type in {"operation", "orderoperation", "routingoperation"}:
        upsert_operation_state(session, event)
        return True
    if aggregate_type == "machine":
        upsert_machine_state(session, event)
        return True
    if aggregate_type == "operator":
        upsert_operator_state(session, event)
        return True
    if aggregate_type in {"inventory", "inventoryitem", "materialitem"}:
        upsert_inventory_state(session, event)
        return True
    return False


def upsert_order_state(session: Session, event: EventStore) -> None:
    state = get_state(session, CurrentOrderState, CurrentOrderState.order_id, event.aggregate_id, event.scenario_id)
    if state is None:
        state = CurrentOrderState(order_id=event.aggregate_id, scenario_id=event.scenario_id)
    update_common_state(state, event, default_status=status_from_event_type(event.event_type, "Order"))
    session.add(state)


def upsert_operation_state(session: Session, event: EventStore) -> None:
    payload = event.payload_json or {}
    state = get_state(session, CurrentOperationState, CurrentOperationState.operation_id, event.aggregate_id, event.scenario_id)
    if state is None:
        state = CurrentOperationState(operation_id=event.aggregate_id, scenario_id=event.scenario_id)
    state.order_id = string_or_none(payload.get("order_id", state.order_id))
    state.machine_id = string_or_none(payload.get("machine_id", state.machine_id))
    state.operator_id = string_or_none(payload.get("operator_id", state.operator_id))
    update_common_state(state, event, default_status=status_from_event_type(event.event_type, "Operation"))
    session.add(state)


def upsert_machine_state(session: Session, event: EventStore) -> None:
    payload = event.payload_json or {}
    state = get_state(session, CurrentMachineState, CurrentMachineState.machine_id, event.aggregate_id, event.scenario_id)
    if state is None:
        state = CurrentMachineState(machine_id=event.aggregate_id, scenario_id=event.scenario_id)
    state.current_operation_id = string_or_none(payload.get("operation_id", state.current_operation_id))
    update_common_state(state, event, default_status=status_from_event_type(event.event_type, "Machine"))
    session.add(state)


def upsert_operator_state(session: Session, event: EventStore) -> None:
    payload = event.payload_json or {}
    state = get_state(session, CurrentOperatorState, CurrentOperatorState.operator_id, event.aggregate_id, event.scenario_id)
    if state is None:
        state = CurrentOperatorState(operator_id=event.aggregate_id, scenario_id=event.scenario_id)
    state.current_operation_id = string_or_none(payload.get("operation_id", state.current_operation_id))
    update_common_state(state, event, default_status=status_from_event_type(event.event_type, "Operator"))
    session.add(state)


def upsert_inventory_state(session: Session, event: EventStore) -> None:
    payload = event.payload_json or {}
    state = get_state(session, CurrentInventoryState, CurrentInventoryState.inventory_item_id, event.aggregate_id, event.scenario_id)
    if state is None:
        state = CurrentInventoryState(inventory_item_id=event.aggregate_id, scenario_id=event.scenario_id)
    state.warehouse_id = string_or_none(payload.get("warehouse_id", state.warehouse_id))
    state.on_hand_qty = float(payload.get("on_hand_qty", state.on_hand_qty))
    state.reserved_qty = float(payload.get("reserved_qty", state.reserved_qty))
    update_common_state(state, event, default_status=status_from_event_type(event.event_type, "Inventory"))
    session.add(state)


def update_common_state(state, event: EventStore, default_status: str) -> None:
    payload = event.payload_json or {}
    state.status = str(payload.get("status") or default_status)
    state.last_event_id = event.event_id
    state.simulation_time = event.simulation_time
    state.updated_at = utc_now()
    state.payload_json = payload


def get_state(
    session: Session,
    model: Type[SQLModel],
    key_column,
    aggregate_id: str,
    scenario_id: int | None,
):
    return session.exec(
        select(model).where(
            key_column == aggregate_id,
            model.scenario_id == scenario_id,
        )
    ).first()


def string_or_none(value) -> str | None:
    if value is None:
        return None
    return str(value)


def status_from_event_type(event_type: str, prefix: str) -> str:
    known_statuses = {
        "OrderCreated": "Created",
        "OrderTreeGenerated": "Planned",
        "ShortageDetected": "MaterialShortage",
        "OperationQueued": "Queued",
        "OperationStarted": "Running",
        "OperationPaused": "Paused",
        "OperationResumed": "Running",
        "OperationFinished": "Finished",
        "MachineReserved": "Reserved",
        "MachineFailed": "Failure",
        "MachineRepairStarted": "Repairing",
        "MachineRepairFinished": "Available",
        "OperatorReserved": "Reserved",
        "MaterialReserved": "Reserved",
        "MaterialArrived": "Available",
    }
    if event_type in known_statuses:
        return known_statuses[event_type]
    if event_type.startswith(prefix):
        return event_type.removeprefix(prefix) or event_type
    return event_type
