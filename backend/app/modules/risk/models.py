from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, JSON, String
from sqlmodel import Field, SQLModel

from app.core.time import utc_now


class RiskRuleSetting(SQLModel, table=True):
    __tablename__ = "risk_rule_settings"

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(index=True, max_length=120)
    value: float = Field(default=0, sa_column=Column("value", Float))
    updated_at: datetime = Field(default_factory=utc_now, sa_column=Column("updated_at", DateTime))


class RiskScore(SQLModel, table=True):
    __tablename__ = "risk_scores"

    id: Optional[int] = Field(default=None, primary_key=True)
    scenario_id: int = Field(index=True)
    aggregate_type: str = Field(index=True, max_length=80)
    aggregate_id: str = Field(index=True, max_length=120)
    total_score: float = Field(default=0, sa_column=Column("total_score", Float))
    level: str = Field(default="Low", max_length=80)
    components_json: dict = Field(default_factory=dict, sa_column=Column("components_json", JSON))
    calculated_at: datetime = Field(default_factory=utc_now, sa_column=Column("calculated_at", DateTime))
