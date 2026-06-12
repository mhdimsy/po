from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.db import get_session
from app.modules.dashboard.schemas import ManagerDashboardRead
from app.modules.dashboard.service import get_manager_dashboard

router = APIRouter(tags=["dashboard"])


@router.get("/manager", response_model=ManagerDashboardRead)
def get_manager_dashboard_endpoint(scenario_id: int | None = None, session: Session = Depends(get_session)):
    return get_manager_dashboard(session, scenario_id=scenario_id)
