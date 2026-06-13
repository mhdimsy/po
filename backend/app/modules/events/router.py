from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.core.db import get_session
from app.modules.events.models import (
    CurrentInventoryState,
    CurrentMachineState,
    CurrentOperationState,
    CurrentOperatorState,
    CurrentOrderState,
    EventStore,
)
from app.modules.events.schemas import (
    CurrentInventoryStateRead,
    CurrentMachineStateRead,
    CurrentOperationStateRead,
    CurrentOperatorStateRead,
    CurrentOrderStateRead,
    EventAppendRequest,
    EventAppendResponse,
    EventRead,
)
from app.modules.events.service import append_event

router = APIRouter(tags=["events-and-state"])


@router.post("", response_model=EventAppendResponse)
def append_event_endpoint(
    request: EventAppendRequest,
    session: Session = Depends(get_session),
):
    return append_event(session, request)


@router.get("", response_model=list[EventRead])
def list_events(
    session: Session = Depends(get_session),
    scenario_id: int | None = None,
    aggregate_type: str | None = None,
    aggregate_id: str | None = None,
    limit: int = Query(100, le=1000),
):
    statement = select(EventStore)
    if scenario_id is not None:
        statement = statement.where(EventStore.scenario_id == scenario_id)
    if aggregate_type is not None:
        statement = statement.where(EventStore.aggregate_type == aggregate_type)
    if aggregate_id is not None:
        statement = statement.where(EventStore.aggregate_id == aggregate_id)
    statement = statement.order_by(EventStore.event_id.desc()).limit(limit)
    return list(session.exec(statement).all())


@router.get("/current/orders", response_model=list[CurrentOrderStateRead])
def list_current_orders(
    session: Session = Depends(get_session),
    scenario_id: int | None = None,
    limit: int = Query(100, le=5000),
):
    statement = select(CurrentOrderState)
    if scenario_id is not None:
        statement = statement.where(CurrentOrderState.scenario_id == scenario_id)
    return list(session.exec(statement.limit(limit)).all())


@router.get("/current/operations", response_model=list[CurrentOperationStateRead])
def list_current_operations(
    session: Session = Depends(get_session),
    scenario_id: int | None = None,
    limit: int = Query(100, le=10000),
):
    statement = select(CurrentOperationState)
    if scenario_id is not None:
        statement = statement.where(CurrentOperationState.scenario_id == scenario_id)
    return list(session.exec(statement.limit(limit)).all())


@router.get("/current/machines", response_model=list[CurrentMachineStateRead])
def list_current_machines(
    session: Session = Depends(get_session),
    scenario_id: int | None = None,
    limit: int = Query(100, le=5000),
):
    statement = select(CurrentMachineState)
    if scenario_id is not None:
        statement = statement.where(CurrentMachineState.scenario_id == scenario_id)
    return list(session.exec(statement.limit(limit)).all())


@router.get("/current/operators", response_model=list[CurrentOperatorStateRead])
def list_current_operators(
    session: Session = Depends(get_session),
    scenario_id: int | None = None,
    limit: int = Query(100, le=5000),
):
    statement = select(CurrentOperatorState)
    if scenario_id is not None:
        statement = statement.where(CurrentOperatorState.scenario_id == scenario_id)
    return list(session.exec(statement.limit(limit)).all())


@router.get("/current/inventory", response_model=list[CurrentInventoryStateRead])
def list_current_inventory(
    session: Session = Depends(get_session),
    scenario_id: int | None = None,
    limit: int = Query(100, le=5000),
):
    statement = select(CurrentInventoryState)
    if scenario_id is not None:
        statement = statement.where(CurrentInventoryState.scenario_id == scenario_id)
    return list(session.exec(statement.limit(limit)).all())
