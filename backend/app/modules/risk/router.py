from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.db import get_session
from app.modules.risk.schemas import RiskCalculationResponse, RiskScoreRead, RiskSettingsRead, RiskSettingsUpdate
from app.modules.risk.service import calculate_risk_scores, get_risk_settings, list_risk_scores, update_risk_settings

router = APIRouter(tags=["risk"])


@router.get("/settings", response_model=RiskSettingsRead)
def get_settings_endpoint(session: Session = Depends(get_session)):
    return get_risk_settings(session)


@router.put("/settings", response_model=RiskSettingsRead)
def update_settings_endpoint(request: RiskSettingsUpdate, session: Session = Depends(get_session)):
    return update_risk_settings(session, request)


@router.post("/calculate/{scenario_id}", response_model=RiskCalculationResponse)
def calculate_risk_endpoint(scenario_id: int, session: Session = Depends(get_session)):
    return calculate_risk_scores(session, scenario_id)


@router.get("/scores", response_model=list[RiskScoreRead])
def list_risk_scores_endpoint(scenario_id: int | None = None, session: Session = Depends(get_session)):
    return list_risk_scores(session, scenario_id=scenario_id)
