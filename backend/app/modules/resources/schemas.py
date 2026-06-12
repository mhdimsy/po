from pydantic import BaseModel, Field


class ShiftRuleInput(BaseModel):
    work_center_id: int | None = None
    shift_code: str
    ratio: float = Field(gt=0)


class GenerateOperatorsRequest(BaseModel):
    count: int = Field(default=500, ge=1, le=10000)
    multi_skill_ratio: float = Field(default=0.25, ge=0, le=1)
    seed: int | None = None
    shift_rules: list[ShiftRuleInput] = Field(default_factory=list)


class DistributionItem(BaseModel):
    work_center_id: int | None
    work_center_title: str
    machine_count: int
    operator_count: int


class GenerateOperatorsResponse(BaseModel):
    requested_count: int
    generated_operators: int
    generated_operator_skills: int
    generated_availability_rows: int
    skills_count: int
    shifts_count: int
    work_center_shift_rules_count: int
    multi_skill_ratio: float
    distribution: list[DistributionItem]


class OperatorRead(BaseModel):
    id: int
    code: str
    full_name: str
    home_work_center_id: int | None
    primary_shift_id: int | None
    status: str
    is_synthetic: bool


class SkillRead(BaseModel):
    id: int
    code: str
    title: str
    process_id: int | None
    is_synthetic: bool


class ShiftRead(BaseModel):
    id: int
    code: str
    title: str
    start_minute_of_day: int
    end_minute_of_day: int
    is_synthetic: bool
