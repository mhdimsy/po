from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, JSON, String
from sqlmodel import Field, SQLModel

from app.core.time import utc_now


class Scenario(SQLModel, table=True):
    __tablename__ = "scenarios"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    base_import_batch_id: Optional[int] = Field(default=None, foreign_key="import_batches.id", index=True)
    parent_scenario_id: Optional[int] = Field(default=None, foreign_key="scenarios.id", index=True)
    base_snapshot_id: Optional[int] = Field(default=None, index=True)
    status: str = Field(default="Draft", max_length=80)
    created_at: datetime = Field(default_factory=utc_now, sa_column=Column("created_at", DateTime))
    settings_json: dict = Field(default_factory=dict, sa_column=Column("settings_json", JSON))
    notes: Optional[str] = Field(default=None, sa_column=Column("notes", String(1000)))


class Snapshot(SQLModel, table=True):
    __tablename__ = "snapshots"

    id: Optional[int] = Field(default=None, primary_key=True)
    scenario_id: int = Field(foreign_key="scenarios.id", index=True)
    snapshot_time: Optional[int] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=utc_now, sa_column=Column("created_at", DateTime))
    reason: str = Field(default="Manual", max_length=255)
    metadata_json: dict = Field(default_factory=dict, sa_column=Column("metadata_json", JSON))
    state_json: dict = Field(default_factory=dict, sa_column=Column("state_json", JSON))
