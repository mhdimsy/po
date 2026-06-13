from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SimulationStartRequest(BaseModel):
    speed_factor: float = Field(default=1, gt=0, le=100)
    start_time: int = Field(default=0, ge=0)


class SimulationStepRequest(BaseModel):
    minutes: int = Field(default=1, ge=1, le=10080)
    process_one_operation: bool = True
    max_operation_transitions: int | None = Field(default=None, ge=1, le=500)


class SimulationRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scenario_id: int
    status: str
    speed_factor: float
    current_sim_time: int
    started_at: datetime
    paused_at: datetime | None
    stopped_at: datetime | None


class SimulationStepResponse(BaseModel):
    run: SimulationRunRead
    events_created: int
    operation_transition: dict[str, Any] | None = None
    operation_transitions: list[dict[str, Any]] = Field(default_factory=list)
