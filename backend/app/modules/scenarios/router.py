from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.core.db import get_session
from app.modules.scenarios.models import Scenario, Snapshot
from app.modules.scenarios.schemas import (
    ScenarioCreateRequest,
    ScenarioForkRequest,
    ProductTreeResponse,
    ScenarioRead,
    ScenarioSeedRequest,
    ScenarioSeedResponse,
    SnapshotCreateRequest,
    SnapshotRead,
)
from app.modules.scenarios.service import create_scenario, create_snapshot, fork_scenario, get_product_tree, seed_scenario_from_master_data

router = APIRouter(tags=["scenarios"])


@router.post("", response_model=ScenarioRead)
def create_scenario_endpoint(
    request: ScenarioCreateRequest,
    session: Session = Depends(get_session),
):
    return create_scenario(session, request)


@router.get("", response_model=list[ScenarioRead])
def list_scenarios(session: Session = Depends(get_session), limit: int = Query(100, le=1000)):
    return list(session.exec(select(Scenario).order_by(Scenario.id.desc()).limit(limit)).all())


@router.post("/{scenario_id}/fork", response_model=ScenarioRead)
def fork_scenario_endpoint(
    scenario_id: int,
    request: ScenarioForkRequest,
    session: Session = Depends(get_session),
):
    return fork_scenario(session, scenario_id, request)


@router.post("/{scenario_id}/seed-from-master-data", response_model=ScenarioSeedResponse)
def seed_scenario_from_master_data_endpoint(
    scenario_id: int,
    request: ScenarioSeedRequest | None = None,
    session: Session = Depends(get_session),
):
    return seed_scenario_from_master_data(session, scenario_id, request or ScenarioSeedRequest())


@router.post("/{scenario_id}/snapshots", response_model=SnapshotRead)
def create_snapshot_endpoint(
    scenario_id: int,
    request: SnapshotCreateRequest | None = None,
    session: Session = Depends(get_session),
):
    return create_snapshot(session, scenario_id, request or SnapshotCreateRequest())


@router.get("/{scenario_id}/product-tree", response_model=ProductTreeResponse)
def get_product_tree_endpoint(
    scenario_id: int,
    root_order_id: str | None = None,
    root_limit: int = Query(25, ge=1, le=100),
    max_depth: int = Query(6, ge=1, le=20),
    session: Session = Depends(get_session),
):
    return get_product_tree(
        session,
        scenario_id=scenario_id,
        root_order_id=root_order_id,
        root_limit=root_limit,
        max_depth=max_depth,
    )


@router.get("/{scenario_id}/snapshots", response_model=list[SnapshotRead])
def list_scenario_snapshots(
    scenario_id: int,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
):
    return list(
        session.exec(
            select(Snapshot)
            .where(Snapshot.scenario_id == scenario_id)
            .order_by(Snapshot.id.desc())
            .limit(limit)
        ).all()
    )


@router.get("/snapshots/all", response_model=list[SnapshotRead])
def list_snapshots(session: Session = Depends(get_session), limit: int = Query(100, le=1000)):
    return list(session.exec(select(Snapshot).order_by(Snapshot.id.desc()).limit(limit)).all())
