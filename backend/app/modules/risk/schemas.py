from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RiskSettingsRead(BaseModel):
    delay_risk_weight: float
    material_shortage_risk_weight: float
    machine_failure_risk_weight: float
    qc_ncr_risk_weight: float
    schedule_instability_weight: float
    low_threshold: float
    medium_threshold: float
    high_threshold: float


class RiskSettingsUpdate(BaseModel):
    delay_risk_weight: float | None = Field(default=None, ge=0)
    material_shortage_risk_weight: float | None = Field(default=None, ge=0)
    machine_failure_risk_weight: float | None = Field(default=None, ge=0)
    qc_ncr_risk_weight: float | None = Field(default=None, ge=0)
    schedule_instability_weight: float | None = Field(default=None, ge=0)
    low_threshold: float | None = Field(default=None, ge=0)
    medium_threshold: float | None = Field(default=None, ge=0)
    high_threshold: float | None = Field(default=None, ge=0)


class RiskScoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scenario_id: int
    aggregate_type: str
    aggregate_id: str
    total_score: float
    level: str
    components_json: dict[str, Any]
    calculated_at: datetime


class RiskCalculationResponse(BaseModel):
    scenario_id: int
    scores_created: int
    scenario_risk: RiskScoreRead
    scores: list[RiskScoreRead]
