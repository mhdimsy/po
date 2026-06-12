from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ScenarioCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    base_import_batch_id: int | None = None
    status: str = Field(default="Draft", max_length=80)
    settings_json: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None


class ScenarioForkRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    base_snapshot_id: int | None = None
    settings_json: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None


class SnapshotCreateRequest(BaseModel):
    reason: str = Field(default="Manual", max_length=255)
    snapshot_time: int | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class ScenarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    base_import_batch_id: int | None
    parent_scenario_id: int | None
    base_snapshot_id: int | None
    status: str
    created_at: datetime
    settings_json: dict[str, Any]
    notes: str | None


class SnapshotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scenario_id: int
    snapshot_time: int | None
    created_at: datetime
    reason: str
    metadata_json: dict[str, Any]
    state_json: dict[str, Any]
