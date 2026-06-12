from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String
from sqlmodel import Field, SQLModel

from app.core.time import utc_now


class OptimizationRun(SQLModel, table=True):
    __tablename__ = "optimization_runs"

    id: Optional[int] = Field(default=None, primary_key=True)
    scenario_id: int = Field(foreign_key="scenarios.id", index=True)
    trigger_type: str = Field(default="Manual", max_length=80)
    policy_json: dict = Field(default_factory=dict, sa_column=Column("policy_json", JSON))
    risk_mode: str = Field(default="Normal", max_length=80)
    frozen_window_minutes: int = Field(default=0, sa_column=Column("frozen_window_minutes", Integer))
    status: str = Field(default="Suggested", max_length=80)
    created_at: datetime = Field(default_factory=utc_now, sa_column=Column("created_at", DateTime))
    score: float = Field(default=0, sa_column=Column("score", Float))
    changed_operations_count: int = Field(default=0, sa_column=Column("changed_operations_count", Integer))
    accepted_at: Optional[datetime] = Field(default=None, sa_column=Column("accepted_at", DateTime))
    rejected_at: Optional[datetime] = Field(default=None, sa_column=Column("rejected_at", DateTime))


class ScheduleOperation(SQLModel, table=True):
    __tablename__ = "schedule_operations"

    id: Optional[int] = Field(default=None, primary_key=True)
    optimization_run_id: int = Field(foreign_key="optimization_runs.id", index=True)
    operation_id: str = Field(index=True, max_length=120)
    order_id: Optional[str] = Field(default=None, index=True, max_length=120)
    machine_id: Optional[str] = Field(default=None, index=True, max_length=120)
    operator_id: Optional[str] = Field(default=None, index=True, max_length=120)
    start_time: int = Field(sa_column=Column("start_time", Integer, index=True))
    end_time: int = Field(sa_column=Column("end_time", Integer, index=True))
    status: str = Field(default="Suggested", max_length=80)
    score: float = Field(default=0, sa_column=Column("score", Float))
    reason_json: dict = Field(default_factory=dict, sa_column=Column("reason_json", JSON))
