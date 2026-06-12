from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlmodel import Field, SQLModel

from app.core.time import utc_now


class Skill(SQLModel, table=True):
    __tablename__ = "skills"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, max_length=80)
    title: str = Field(max_length=255)
    process_id: Optional[int] = Field(default=None, sa_column=Column("Process_Id", Integer, index=True))
    is_synthetic: bool = Field(default=True, sa_column=Column("IsSynthetic", Boolean))


class Shift(SQLModel, table=True):
    __tablename__ = "shifts"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, max_length=80)
    title: str = Field(max_length=255)
    start_minute_of_day: int = Field(sa_column=Column("StartMinuteOfDay", Integer))
    end_minute_of_day: int = Field(sa_column=Column("EndMinuteOfDay", Integer))
    is_synthetic: bool = Field(default=True, sa_column=Column("IsSynthetic", Boolean))


class WorkCenterShiftRule(SQLModel, table=True):
    __tablename__ = "work_center_shift_rules"

    id: Optional[int] = Field(default=None, primary_key=True)
    work_center_id: Optional[int] = Field(default=None, sa_column=Column("WorkCenter_Id", Integer, index=True))
    shift_id: int = Field(foreign_key="shifts.id", index=True)
    ratio: float = Field(default=1)
    is_synthetic: bool = Field(default=True, sa_column=Column("IsSynthetic", Boolean))


class Operator(SQLModel, table=True):
    __tablename__ = "operators"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, max_length=80)
    full_name: str = Field(max_length=255)
    home_work_center_id: Optional[int] = Field(default=None, sa_column=Column("HomeWorkCenter_Id", Integer, index=True))
    primary_shift_id: Optional[int] = Field(default=None, foreign_key="shifts.id", index=True)
    status: str = Field(default="Available", max_length=80)
    is_synthetic: bool = Field(default=True, sa_column=Column("IsSynthetic", Boolean))
    generated_at: datetime = Field(default_factory=utc_now, sa_column=Column("GeneratedAt", DateTime))


class OperatorSkill(SQLModel, table=True):
    __tablename__ = "operator_skills"

    id: Optional[int] = Field(default=None, primary_key=True)
    operator_id: int = Field(foreign_key="operators.id", index=True)
    skill_id: int = Field(foreign_key="skills.id", index=True)
    level: int = Field(sa_column=Column("Level", Integer))
    is_primary: bool = Field(default=False, sa_column=Column("IsPrimary", Boolean))


class OperatorAvailability(SQLModel, table=True):
    __tablename__ = "operator_availability"

    id: Optional[int] = Field(default=None, primary_key=True)
    operator_id: int = Field(foreign_key="operators.id", index=True)
    work_center_id: Optional[int] = Field(default=None, sa_column=Column("WorkCenter_Id", Integer, index=True))
    shift_id: int = Field(foreign_key="shifts.id", index=True)
    status: str = Field(default="Available", max_length=80)
    valid_from: datetime = Field(default_factory=utc_now, sa_column=Column("ValidFrom", DateTime))
    valid_to: Optional[datetime] = Field(default=None, sa_column=Column("ValidTo", DateTime))
