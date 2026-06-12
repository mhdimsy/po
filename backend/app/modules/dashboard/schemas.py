from typing import Any

from pydantic import BaseModel

from app.modules.risk.schemas import RiskScoreRead


class DeliverySummary(BaseModel):
    total_orders: int
    completed_orders: int
    delayed_orders: int
    on_time_rate_percent: float


class DelaySummary(BaseModel):
    delayed_operations: int
    waiting_material_operations: int
    waiting_machine_operations: int
    waiting_qc_operations: int


class ProductionProgressSummary(BaseModel):
    total_operations: int
    finished_operations: int
    active_operations: int
    queued_operations: int
    completion_percent: float


class CapacitySummary(BaseModel):
    total_machines: int
    busy_machines: int
    unavailable_machines: int
    machine_utilization_percent: float
    total_operators: int
    busy_operators: int
    operator_utilization_percent: float


class BottleneckItem(BaseModel):
    resource_id: str
    queued_operations: int


class MaterialShortageSummary(BaseModel):
    shortage_items: int
    reserved_items: int
    open_purchase_requests: int
    top_shortages: list[dict[str, Any]]


class NcrReworkSummary(BaseModel):
    open_ncrs: int
    high_severity_ncrs: int
    active_rework_orders: int
    estimated_delay_min: int


class OptimizerPerformanceSummary(BaseModel):
    latest_run_id: int | None
    status: str | None
    score: float | None
    changed_operations_count: int
    suggested_operations: int
    accepted_operations: int


class ManagerDashboardRead(BaseModel):
    scenario_id: int | None
    delivery: DeliverySummary
    delay: DelaySummary
    production_progress: ProductionProgressSummary
    capacity: CapacitySummary
    bottleneck: list[BottleneckItem]
    material_shortage: MaterialShortageSummary
    ncr_rework: NcrReworkSummary
    optimizer_performance: OptimizerPerformanceSummary
    risk: list[RiskScoreRead]
