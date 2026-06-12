from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlmodel import Field, SQLModel

from app.core.time import utc_now


class SimulationRun(SQLModel, table=True):
    __tablename__ = "simulation_runs"

    id: Optional[int] = Field(default=None, primary_key=True)
    scenario_id: int = Field(foreign_key="scenarios.id", index=True)
    status: str = Field(default="Running", max_length=80)
    speed_factor: float = Field(default=1, sa_column=Column("speed_factor", Float))
    current_sim_time: int = Field(default=0, sa_column=Column("current_sim_time", Integer, index=True))
    started_at: datetime = Field(default_factory=utc_now, sa_column=Column("started_at", DateTime))
    paused_at: Optional[datetime] = Field(default=None, sa_column=Column("paused_at", DateTime))
    stopped_at: Optional[datetime] = Field(default=None, sa_column=Column("stopped_at", DateTime))
