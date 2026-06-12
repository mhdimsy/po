from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.db import get_session
from app.modules.optimizer.schemas import AcceptScheduleResponse, OptimizationRunRead, OptimizerRunRequest, OptimizerRunResponse, ScheduleOperationRead
from app.modules.optimizer.service import accept_schedule, list_optimizer_runs, list_schedule, run_optimizer

router = APIRouter(tags=["optimizer"])


@router.post("/run", response_model=OptimizerRunResponse)
def run_optimizer_endpoint(
    request: OptimizerRunRequest,
    session: Session = Depends(get_session),
):
    return run_optimizer(session, request)


@router.get("/runs", response_model=list[OptimizationRunRead])
def list_optimizer_runs_endpoint(
    scenario_id: int | None = None,
    session: Session = Depends(get_session),
):
    return list_optimizer_runs(session, scenario_id=scenario_id)


@router.get("/runs/{optimization_run_id}/schedule", response_model=list[ScheduleOperationRead])
def list_schedule_endpoint(
    optimization_run_id: int,
    session: Session = Depends(get_session),
):
    return list_schedule(session, optimization_run_id)


@router.post("/runs/{optimization_run_id}/accept", response_model=AcceptScheduleResponse)
def accept_schedule_endpoint(
    optimization_run_id: int,
    session: Session = Depends(get_session),
):
    return accept_schedule(session, optimization_run_id)
