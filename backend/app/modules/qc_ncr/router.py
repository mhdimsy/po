from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.db import get_session
from app.modules.qc_ncr.schemas import (
    ApprovalDecisionRequest,
    NcrApprovalRead,
    NcrRead,
    QcCheckRead,
    QcResultRequest,
    QcResultResponse,
    QcStartRequest,
)
from app.modules.qc_ncr.service import (
    decide_approval,
    list_approvals,
    list_ncrs,
    list_qc_checks,
    start_qc,
    submit_qc_result,
)

router = APIRouter(tags=["qc-ncr-approval"])


@router.post("/checks", response_model=QcCheckRead)
def start_qc_endpoint(request: QcStartRequest, session: Session = Depends(get_session)):
    return start_qc(session, request)


@router.post("/checks/{qc_check_id}/result", response_model=QcResultResponse)
def submit_qc_result_endpoint(
    qc_check_id: int,
    request: QcResultRequest,
    session: Session = Depends(get_session),
):
    return submit_qc_result(session, qc_check_id, request)


@router.get("/checks", response_model=list[QcCheckRead])
def list_qc_checks_endpoint(scenario_id: int | None = None, session: Session = Depends(get_session)):
    return list_qc_checks(session, scenario_id=scenario_id)


@router.get("/ncrs", response_model=list[NcrRead])
def list_ncrs_endpoint(scenario_id: int | None = None, session: Session = Depends(get_session)):
    return list_ncrs(session, scenario_id=scenario_id)


@router.get("/approvals", response_model=list[NcrApprovalRead])
def list_approvals_endpoint(ncr_id: int | None = None, session: Session = Depends(get_session)):
    return list_approvals(session, ncr_id=ncr_id)


@router.post("/approvals/{approval_id}/decision", response_model=NcrApprovalRead)
def decide_approval_endpoint(
    approval_id: int,
    request: ApprovalDecisionRequest,
    session: Session = Depends(get_session),
):
    return decide_approval(session, approval_id, request)
