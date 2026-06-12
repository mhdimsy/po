from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String
from sqlmodel import Field, SQLModel

from app.core.time import utc_now


class QcCheck(SQLModel, table=True):
    __tablename__ = "qc_checks"

    id: Optional[int] = Field(default=None, primary_key=True)
    scenario_id: int = Field(index=True)
    operation_id: str = Field(index=True, max_length=120)
    status: str = Field(default="Open", max_length=80)
    result: Optional[str] = Field(default=None, max_length=80)
    disposition: Optional[str] = Field(default=None, max_length=80)
    created_at: datetime = Field(default_factory=utc_now, sa_column=Column("created_at", DateTime))
    completed_at: Optional[datetime] = Field(default=None, sa_column=Column("completed_at", DateTime))
    metadata_json: dict = Field(default_factory=dict, sa_column=Column("metadata_json", JSON))


class Ncr(SQLModel, table=True):
    __tablename__ = "ncrs"

    id: Optional[int] = Field(default=None, primary_key=True)
    scenario_id: int = Field(index=True)
    code: str = Field(index=True, max_length=120)
    qc_check_id: Optional[int] = Field(default=None, foreign_key="qc_checks.id", index=True)
    related_order_id: Optional[str] = Field(default=None, index=True, max_length=120)
    related_operation_id: Optional[str] = Field(default=None, index=True, max_length=120)
    related_material_id: Optional[str] = Field(default=None, index=True, max_length=120)
    severity: str = Field(default="Medium", max_length=80)
    defect_type: str = Field(default="Unspecified", max_length=120)
    root_cause: Optional[str] = Field(default=None, max_length=255)
    responsible_area: Optional[str] = Field(default=None, max_length=120)
    status: str = Field(default="Open", max_length=80)
    disposition: Optional[str] = Field(default=None, max_length=80)
    impact_type: Optional[str] = Field(default=None, max_length=80)
    estimated_delay_min: int = Field(default=0, sa_column=Column("estimated_delay_min", Integer))
    required_approvals_json: dict = Field(default_factory=dict, sa_column=Column("required_approvals_json", JSON))
    created_at: datetime = Field(default_factory=utc_now, sa_column=Column("created_at", DateTime))
    closed_at: Optional[datetime] = Field(default=None, sa_column=Column("closed_at", DateTime))


class NcrApproval(SQLModel, table=True):
    __tablename__ = "ncr_approvals"

    id: Optional[int] = Field(default=None, primary_key=True)
    ncr_id: int = Field(foreign_key="ncrs.id", index=True)
    step_name: str = Field(index=True, max_length=120)
    status: str = Field(default="Pending", max_length=80)
    expected_duration_min: int = Field(default=60, sa_column=Column("expected_duration_min", Integer))
    requested_at: datetime = Field(default_factory=utc_now, sa_column=Column("requested_at", DateTime))
    decided_at: Optional[datetime] = Field(default=None, sa_column=Column("decided_at", DateTime))
    decision_note: Optional[str] = Field(default=None, max_length=1000)


class ReworkOrder(SQLModel, table=True):
    __tablename__ = "rework_orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    scenario_id: int = Field(index=True)
    ncr_id: int = Field(foreign_key="ncrs.id", index=True)
    source_operation_id: str = Field(index=True, max_length=120)
    rework_route: str = Field(default="SimpleRework", max_length=120)
    status: str = Field(default="Created", max_length=80)
    created_at: datetime = Field(default_factory=utc_now, sa_column=Column("created_at", DateTime))


class ReplacementOrder(SQLModel, table=True):
    __tablename__ = "replacement_orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    scenario_id: int = Field(index=True)
    ncr_id: int = Field(foreign_key="ncrs.id", index=True)
    source_order_id: Optional[str] = Field(default=None, index=True, max_length=120)
    source_operation_id: Optional[str] = Field(default=None, index=True, max_length=120)
    status: str = Field(default="Created", max_length=80)
    created_at: datetime = Field(default_factory=utc_now, sa_column=Column("created_at", DateTime))
