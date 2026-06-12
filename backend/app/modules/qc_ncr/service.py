from __future__ import annotations

from sqlmodel import Session, select

from app.core.time import utc_now
from app.modules.events.models import CurrentOperationState
from app.modules.events.schemas import EventAppendRequest
from app.modules.events.service import append_event
from app.modules.qc_ncr.models import Ncr, NcrApproval, QcCheck, ReplacementOrder, ReworkOrder
from app.modules.qc_ncr.schemas import ApprovalDecisionRequest, QcResultRequest, QcResultResponse, QcStartRequest


APPROVAL_STEPS = ["QC", "Engineering", "Production Manager"]


def start_qc(session: Session, request: QcStartRequest) -> QcCheck:
    qc_check = QcCheck(
        scenario_id=request.scenario_id,
        operation_id=request.operation_id,
        status="Open",
        metadata_json=request.metadata_json,
    )
    session.add(qc_check)
    session.flush()
    append_event(
        session,
        EventAppendRequest(
            event_type="QCStarted",
            aggregate_type="Operation",
            aggregate_id=request.operation_id,
            scenario_id=request.scenario_id,
            payload_json={"status": "QC", "qc_check_id": qc_check.id},
        ),
    )
    session.refresh(qc_check)
    return qc_check


def submit_qc_result(session: Session, qc_check_id: int, request: QcResultRequest) -> QcResultResponse:
    qc_check = require_qc_check(session, qc_check_id)
    qc_check.result = request.result
    qc_check.disposition = request.disposition
    qc_check.completed_at = utc_now()

    if request.result == "Pass":
        qc_check.status = "Passed"
        session.add(qc_check)
        append_event(
            session,
            EventAppendRequest(
                event_type="QCPassed",
                aggregate_type="Operation",
                aggregate_id=qc_check.operation_id,
                scenario_id=qc_check.scenario_id,
                payload_json={"status": "Finished", "qc_check_id": qc_check.id},
            ),
        )
        session.refresh(qc_check)
        return QcResultResponse(qc_check=qc_check, path_created="Pass")

    qc_check.status = "Failed"
    session.add(qc_check)
    append_event(
        session,
        EventAppendRequest(
            event_type="QCFailed",
            aggregate_type="Operation",
            aggregate_id=qc_check.operation_id,
            scenario_id=qc_check.scenario_id,
            payload_json={"status": "BlockedByNCR", "qc_check_id": qc_check.id, "disposition": request.disposition},
        ),
    )

    ncr = create_ncr_from_qc(session, qc_check, request)
    approvals = create_approval_steps(session, ncr)
    path_created = create_fail_path(session, qc_check, ncr, request.disposition)

    session.refresh(qc_check)
    session.refresh(ncr)
    for approval in approvals:
        session.refresh(approval)
    return QcResultResponse(qc_check=qc_check, ncr=ncr, approvals=approvals, path_created=path_created)


def create_ncr_from_qc(session: Session, qc_check: QcCheck, request: QcResultRequest) -> Ncr:
    operation = get_operation(session, qc_check.scenario_id, qc_check.operation_id)
    ncr = Ncr(
        scenario_id=qc_check.scenario_id,
        code=f"NCR-{qc_check.scenario_id}-{qc_check.id}",
        qc_check_id=qc_check.id,
        related_order_id=operation.order_id if operation else None,
        related_operation_id=qc_check.operation_id,
        severity=request.severity,
        defect_type=request.defect_type,
        root_cause=request.root_cause,
        responsible_area=request.responsible_area,
        status="WaitingApproval",
        disposition=request.disposition,
        impact_type=request.disposition,
        estimated_delay_min=request.estimated_delay_min,
        required_approvals_json={"steps": APPROVAL_STEPS},
    )
    session.add(ncr)
    session.flush()
    append_event(
        session,
        EventAppendRequest(
            event_type="NCROpened",
            aggregate_type="Operation",
            aggregate_id=qc_check.operation_id,
            scenario_id=qc_check.scenario_id,
            payload_json={
                "status": "BlockedByNCR",
                "ncr_id": ncr.id,
                "ncr_code": ncr.code,
                "disposition": request.disposition,
            },
        ),
    )
    return ncr


def create_approval_steps(session: Session, ncr: Ncr) -> list[NcrApproval]:
    approvals: list[NcrApproval] = []
    for index, step in enumerate(APPROVAL_STEPS, start=1):
        approval = NcrApproval(
            ncr_id=ncr.id,
            step_name=step,
            status="Pending",
            expected_duration_min=60 * index,
        )
        session.add(approval)
        session.flush()
        approvals.append(approval)
        append_event(
            session,
            EventAppendRequest(
                event_type="NCRApprovalRequested",
                aggregate_type="Operation",
                aggregate_id=ncr.related_operation_id or str(ncr.id),
                scenario_id=ncr.scenario_id,
                payload_json={
                    "status": "WaitingQCApproval",
                    "ncr_id": ncr.id,
                    "approval_id": approval.id,
                    "step_name": approval.step_name,
                },
            ),
        )
    return approvals


def create_fail_path(session: Session, qc_check: QcCheck, ncr: Ncr, disposition: str) -> str:
    if disposition in {"SimpleRework", "ReworkRoute"}:
        rework = ReworkOrder(
            scenario_id=qc_check.scenario_id,
            ncr_id=ncr.id,
            source_operation_id=qc_check.operation_id,
            rework_route=disposition,
        )
        session.add(rework)
        session.flush()
        append_event(
            session,
            EventAppendRequest(
                event_type="ReworkCreated",
                aggregate_type="Operation",
                aggregate_id=qc_check.operation_id,
                scenario_id=qc_check.scenario_id,
                payload_json={"status": "Rework", "ncr_id": ncr.id, "rework_order_id": rework.id},
            ),
        )
        return disposition
    if disposition == "Scrap":
        append_event(
            session,
            EventAppendRequest(
                event_type="NCRDispositionDecided",
                aggregate_type="Operation",
                aggregate_id=qc_check.operation_id,
                scenario_id=qc_check.scenario_id,
                payload_json={"status": "Scrap", "ncr_id": ncr.id, "disposition": "Scrap"},
            ),
        )
        return "Scrap"
    if disposition == "Replacement":
        operation = get_operation(session, qc_check.scenario_id, qc_check.operation_id)
        replacement = ReplacementOrder(
            scenario_id=qc_check.scenario_id,
            ncr_id=ncr.id,
            source_order_id=operation.order_id if operation else None,
            source_operation_id=qc_check.operation_id,
        )
        session.add(replacement)
        session.flush()
        append_event(
            session,
            EventAppendRequest(
                event_type="ReplacementOrderCreated",
                aggregate_type="Operation",
                aggregate_id=qc_check.operation_id,
                scenario_id=qc_check.scenario_id,
                payload_json={"status": "WaitingReplacement", "ncr_id": ncr.id, "replacement_order_id": replacement.id},
            ),
        )
        return "Replacement"
    return "NCR"


def decide_approval(session: Session, approval_id: int, request: ApprovalDecisionRequest) -> NcrApproval:
    approval = session.get(NcrApproval, approval_id)
    if approval is None:
        raise RuntimeError(f"NcrApproval {approval_id} was not found.")
    ncr = session.get(Ncr, approval.ncr_id)
    if ncr is None:
        raise RuntimeError(f"NCR {approval.ncr_id} was not found.")

    approval.status = request.decision
    approval.decided_at = utc_now()
    approval.decision_note = request.decision_note
    session.add(approval)

    event_type = "NCRApproved" if request.decision == "Approved" else "NCRRejected"
    append_event(
        session,
        EventAppendRequest(
            event_type=event_type,
            aggregate_type="Operation",
            aggregate_id=ncr.related_operation_id or str(ncr.id),
            scenario_id=ncr.scenario_id,
            payload_json={
                "status": "WaitingQCApproval" if request.decision == "Approved" else "BlockedByNCR",
                "ncr_id": ncr.id,
                "approval_id": approval.id,
                "step_name": approval.step_name,
            },
        ),
    )
    update_ncr_after_decision(session, ncr)
    session.refresh(approval)
    return approval


def update_ncr_after_decision(session: Session, ncr: Ncr) -> None:
    approvals = list(session.exec(select(NcrApproval).where(NcrApproval.ncr_id == ncr.id)).all())
    if any(approval.status == "Rejected" for approval in approvals):
        ncr.status = "Rejected"
        session.add(ncr)
        return
    if approvals and all(approval.status == "Approved" for approval in approvals):
        ncr.status = "Approved"
        ncr.closed_at = utc_now()
        session.add(ncr)
        append_event(
            session,
            EventAppendRequest(
                event_type="NCRDispositionDecided",
                aggregate_type="Operation",
                aggregate_id=ncr.related_operation_id or str(ncr.id),
                scenario_id=ncr.scenario_id,
                payload_json={"status": "Rework" if ncr.disposition in {"SimpleRework", "ReworkRoute"} else "Finished", "ncr_id": ncr.id},
            ),
        )


def list_qc_checks(session: Session, scenario_id: int | None = None) -> list[QcCheck]:
    statement = select(QcCheck).order_by(QcCheck.id.desc())
    if scenario_id is not None:
        statement = statement.where(QcCheck.scenario_id == scenario_id)
    return list(session.exec(statement).all())


def list_ncrs(session: Session, scenario_id: int | None = None) -> list[Ncr]:
    statement = select(Ncr).order_by(Ncr.id.desc())
    if scenario_id is not None:
        statement = statement.where(Ncr.scenario_id == scenario_id)
    return list(session.exec(statement).all())


def list_approvals(session: Session, ncr_id: int | None = None) -> list[NcrApproval]:
    statement = select(NcrApproval).order_by(NcrApproval.id)
    if ncr_id is not None:
        statement = statement.where(NcrApproval.ncr_id == ncr_id)
    return list(session.exec(statement).all())


def require_qc_check(session: Session, qc_check_id: int) -> QcCheck:
    qc_check = session.get(QcCheck, qc_check_id)
    if qc_check is None:
        raise RuntimeError(f"QcCheck {qc_check_id} was not found.")
    return qc_check


def get_operation(session: Session, scenario_id: int, operation_id: str) -> CurrentOperationState | None:
    return session.exec(
        select(CurrentOperationState)
        .where(CurrentOperationState.scenario_id == scenario_id)
        .where(CurrentOperationState.operation_id == operation_id)
    ).first()
