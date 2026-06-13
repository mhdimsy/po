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


class ScenarioSeedRequest(BaseModel):
    import_batch_id: int | None = None
    max_orders: int = Field(default=500, ge=1, le=5000)
    reset_existing_state: bool = True


class ScenarioSeedResponse(BaseModel):
    scenario_id: int
    import_batch_id: int
    orders_seeded: int
    operations_seeded: int
    machines_seeded: int
    skipped_orders_without_routing: int
    max_orders: int


class ProductTreeOperationSummary(BaseModel):
    total: int
    queued: int
    setup: int
    running: int
    finished: int
    blocked: int
    other: int


class ProductTreeNode(BaseModel):
    order_id: str
    order_code: str | None = None
    product_code: str | None = None
    status: str
    computed_status: str
    assignment_status: str | None = None
    operation_summary: ProductTreeOperationSummary
    children: list["ProductTreeNode"] = Field(default_factory=list)


class ProductTreeResponse(BaseModel):
    scenario_id: int
    root_count: int
    total_orders_in_scope: int
    max_depth: int
    roots: list[ProductTreeNode]


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
