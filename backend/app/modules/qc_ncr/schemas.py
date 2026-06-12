from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class QcStartRequest(BaseModel):
    scenario_id: int
    operation_id: str = Field(min_length=1, max_length=120)
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class QcResultRequest(BaseModel):
    result: str = Field(pattern="^(Pass|Fail)$")
    disposition: str = Field(default="NCR", pattern="^(NCR|SimpleRework|ReworkRoute|Scrap|Replacement)$")
    severity: str = Field(default="Medium", max_length=80)
    defect_type: str = Field(default="Unspecified", max_length=120)
    root_cause: str | None = None
    responsible_area: str | None = None
    estimated_delay_min: int = Field(default=0, ge=0)


class ApprovalDecisionRequest(BaseModel):
    decision: str = Field(pattern="^(Approved|Rejected)$")
    decision_note: str | None = None


class QcCheckRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scenario_id: int
    operation_id: str
    status: str
    result: str | None
    disposition: str | None
    created_at: datetime
    completed_at: datetime | None
    metadata_json: dict[str, Any]


class NcrRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scenario_id: int
    code: str
    qc_check_id: int | None
    related_order_id: str | None
    related_operation_id: str | None
    severity: str
    defect_type: str
    status: str
    disposition: str | None
    estimated_delay_min: int


class NcrApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ncr_id: int
    step_name: str
    status: str
    expected_duration_min: int
    requested_at: datetime
    decided_at: datetime | None
    decision_note: str | None


class QcResultResponse(BaseModel):
    qc_check: QcCheckRead
    ncr: NcrRead | None = None
    approvals: list[NcrApprovalRead] = []
    path_created: str | None = None
