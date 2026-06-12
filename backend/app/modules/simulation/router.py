from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.db import get_session
from app.modules.simulation.schemas import SimulationRunRead, SimulationStartRequest, SimulationStepRequest, SimulationStepResponse
from app.modules.simulation.service import (
    list_simulation_runs,
    pause_simulation,
    resume_simulation,
    start_simulation,
    step_simulation,
)

router = APIRouter(tags=["simulation"])


@router.post("/{scenario_id}/start", response_model=SimulationRunRead)
def start_simulation_endpoint(
    scenario_id: int,
    request: SimulationStartRequest | None = None,
    session: Session = Depends(get_session),
):
    return start_simulation(session, scenario_id, request or SimulationStartRequest())


@router.post("/{scenario_id}/pause", response_model=SimulationRunRead)
def pause_simulation_endpoint(scenario_id: int, session: Session = Depends(get_session)):
    return pause_simulation(session, scenario_id)


@router.post("/{scenario_id}/resume", response_model=SimulationRunRead)
def resume_simulation_endpoint(scenario_id: int, session: Session = Depends(get_session)):
    return resume_simulation(session, scenario_id)


@router.post("/{scenario_id}/step", response_model=SimulationStepResponse)
def step_simulation_endpoint(
    scenario_id: int,
    request: SimulationStepRequest | None = None,
    session: Session = Depends(get_session),
):
    return step_simulation(session, scenario_id, request or SimulationStepRequest())


@router.get("/{scenario_id}/runs", response_model=list[SimulationRunRead])
def list_simulation_runs_endpoint(scenario_id: int, session: Session = Depends(get_session)):
    return list_simulation_runs(session, scenario_id)
