from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, JSON, String
from sqlmodel import Field, SQLModel

from app.core.time import utc_now


class EventStore(SQLModel, table=True):
    __tablename__ = "event_store"

    event_id: Optional[int] = Field(default=None, primary_key=True)
    event_type: str = Field(index=True, max_length=120)
    aggregate_type: str = Field(index=True, max_length=120)
    aggregate_id: str = Field(index=True, max_length=120)
    scenario_id: Optional[int] = Field(default=None, index=True)
    payload_json: dict = Field(default_factory=dict, sa_column=Column("payload_json", JSON))
    simulation_time: Optional[int] = Field(default=None, sa_column=Column("simulation_time", Integer, index=True))
    created_at: datetime = Field(default_factory=utc_now, sa_column=Column("created_at", DateTime, index=True))


class CurrentOrderState(SQLModel, table=True):
    __tablename__ = "current_order_states"

    id: Optional[int] = Field(default=None, primary_key=True)
    scenario_id: Optional[int] = Field(default=None, index=True)
    order_id: str = Field(index=True, max_length=120)
    status: str = Field(default="Created", max_length=80)
    last_event_id: Optional[int] = Field(default=None, foreign_key="event_store.event_id")
    simulation_time: Optional[int] = Field(default=None, index=True)
    updated_at: datetime = Field(default_factory=utc_now, sa_column=Column("updated_at", DateTime))
    payload_json: dict = Field(default_factory=dict, sa_column=Column("payload_json", JSON))


class CurrentOperationState(SQLModel, table=True):
    __tablename__ = "current_operation_states"

    id: Optional[int] = Field(default=None, primary_key=True)
    scenario_id: Optional[int] = Field(default=None, index=True)
    operation_id: str = Field(index=True, max_length=120)
    order_id: Optional[str] = Field(default=None, index=True, max_length=120)
    machine_id: Optional[str] = Field(default=None, index=True, max_length=120)
    operator_id: Optional[str] = Field(default=None, index=True, max_length=120)
    status: str = Field(default="Queued", max_length=80)
    last_event_id: Optional[int] = Field(default=None, foreign_key="event_store.event_id")
    simulation_time: Optional[int] = Field(default=None, index=True)
    updated_at: datetime = Field(default_factory=utc_now, sa_column=Column("updated_at", DateTime))
    payload_json: dict = Field(default_factory=dict, sa_column=Column("payload_json", JSON))


class CurrentMachineState(SQLModel, table=True):
    __tablename__ = "current_machine_states"

    id: Optional[int] = Field(default=None, primary_key=True)
    scenario_id: Optional[int] = Field(default=None, index=True)
    machine_id: str = Field(index=True, max_length=120)
    status: str = Field(default="Available", max_length=80)
    current_operation_id: Optional[str] = Field(default=None, index=True, max_length=120)
    last_event_id: Optional[int] = Field(default=None, foreign_key="event_store.event_id")
    simulation_time: Optional[int] = Field(default=None, index=True)
    updated_at: datetime = Field(default_factory=utc_now, sa_column=Column("updated_at", DateTime))
    payload_json: dict = Field(default_factory=dict, sa_column=Column("payload_json", JSON))


class CurrentOperatorState(SQLModel, table=True):
    __tablename__ = "current_operator_states"

    id: Optional[int] = Field(default=None, primary_key=True)
    scenario_id: Optional[int] = Field(default=None, index=True)
    operator_id: str = Field(index=True, max_length=120)
    status: str = Field(default="Available", max_length=80)
    current_operation_id: Optional[str] = Field(default=None, index=True, max_length=120)
    last_event_id: Optional[int] = Field(default=None, foreign_key="event_store.event_id")
    simulation_time: Optional[int] = Field(default=None, index=True)
    updated_at: datetime = Field(default_factory=utc_now, sa_column=Column("updated_at", DateTime))
    payload_json: dict = Field(default_factory=dict, sa_column=Column("payload_json", JSON))


class CurrentInventoryState(SQLModel, table=True):
    __tablename__ = "current_inventory_states"

    id: Optional[int] = Field(default=None, primary_key=True)
    scenario_id: Optional[int] = Field(default=None, index=True)
    inventory_item_id: str = Field(index=True, max_length=120)
    warehouse_id: Optional[str] = Field(default=None, index=True, max_length=120)
    on_hand_qty: float = 0
    reserved_qty: float = 0
    status: str = Field(default="Available", max_length=80)
    last_event_id: Optional[int] = Field(default=None, foreign_key="event_store.event_id")
    simulation_time: Optional[int] = Field(default=None, index=True)
    updated_at: datetime = Field(default_factory=utc_now, sa_column=Column("updated_at", DateTime))
    payload_json: dict = Field(default_factory=dict, sa_column=Column("payload_json", JSON))
