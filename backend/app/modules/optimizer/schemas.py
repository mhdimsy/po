from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class OptimizerRunRequest(BaseModel):
    scenario_id: int
    trigger_type: str = Field(default="Manual", max_length=80)
    policy_json: dict[str, Any] = Field(default_factory=dict)
    risk_mode: str = Field(default="Normal", max_length=80)
    frozen_window_minutes: int = Field(default=0, ge=0)
    horizon_minutes: int = Field(default=10080, ge=1)


class OptimizationRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scenario_id: int
    trigger_type: str
    policy_json: dict[str, Any]
    risk_mode: str
    frozen_window_minutes: int
    status: str
    created_at: datetime
    score: float
    changed_operations_count: int
    accepted_at: datetime | None
    rejected_at: datetime | None


class ScheduleOperationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    optimization_run_id: int
    operation_id: str
    order_id: str | None
    machine_id: str | None
    operator_id: str | None
    start_time: int
    end_time: int
    status: str
    score: float
    reason_json: dict[str, Any]


class OptimizerRunResponse(BaseModel):
    run: OptimizationRunRead
    schedule: list[ScheduleOperationRead]


class AcceptScheduleResponse(BaseModel):
    run: OptimizationRunRead
    accepted_operations: int
