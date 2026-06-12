from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventAppendRequest(BaseModel):
    event_type: str = Field(min_length=1, max_length=120)
    aggregate_type: str = Field(min_length=1, max_length=120)
    aggregate_id: str = Field(min_length=1, max_length=120)
    scenario_id: int | None = None
    payload_json: dict[str, Any] = Field(default_factory=dict)
    simulation_time: int | None = None
    update_current_state: bool = True


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: int
    event_type: str
    aggregate_type: str
    aggregate_id: str
    scenario_id: int | None
    payload_json: dict[str, Any]
    simulation_time: int | None
    created_at: datetime


class EventAppendResponse(BaseModel):
    event: EventRead
    current_state_updated: bool


class CurrentStateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scenario_id: int | None
    status: str
    last_event_id: int | None
    simulation_time: int | None
    updated_at: datetime
    payload_json: dict[str, Any]


class CurrentOrderStateRead(CurrentStateRead):
    order_id: str


class CurrentOperationStateRead(CurrentStateRead):
    operation_id: str
    order_id: str | None
    machine_id: str | None
    operator_id: str | None


class CurrentMachineStateRead(CurrentStateRead):
    machine_id: str
    current_operation_id: str | None


class CurrentOperatorStateRead(CurrentStateRead):
    operator_id: str
    current_operation_id: str | None


class CurrentInventoryStateRead(CurrentStateRead):
    inventory_item_id: str
    warehouse_id: str | None
    on_hand_qty: float
    reserved_qty: float
