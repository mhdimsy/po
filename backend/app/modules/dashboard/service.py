from __future__ import annotations

from collections import Counter
from typing import Iterable

from sqlmodel import Session, select

from app.modules.dashboard.schemas import (
    BottleneckItem,
    CapacitySummary,
    DelaySummary,
    DeliverySummary,
    ManagerDashboardRead,
    MaterialShortageSummary,
    NcrReworkSummary,
    OptimizerPerformanceSummary,
    ProductionProgressSummary,
)
from app.modules.events.models import (
    CurrentInventoryState,
    CurrentMachineState,
    CurrentOperationState,
    CurrentOperatorState,
    CurrentOrderState,
)
from app.modules.materials.models import PurchaseRequest
from app.modules.optimizer.models import OptimizationRun, ScheduleOperation
from app.modules.qc_ncr.models import Ncr, ReworkOrder
from app.modules.risk.service import list_risk_scores


def get_manager_dashboard(session: Session, scenario_id: int | None = None) -> ManagerDashboardRead:
    orders = scoped(session, CurrentOrderState, scenario_id)
    operations = scoped(session, CurrentOperationState, scenario_id)
    machines = scoped(session, CurrentMachineState, scenario_id)
    operators = scoped(session, CurrentOperatorState, scenario_id)
    inventory_states = scoped(session, CurrentInventoryState, scenario_id)
    ncrs = scoped(session, Ncr, scenario_id)
    rework_orders = scoped(session, ReworkOrder, scenario_id)
    latest_run = latest_optimizer_run(session, scenario_id)
    schedule_operations = optimizer_schedule_operations(session, latest_run)
    risks = list_risk_scores(session, scenario_id=scenario_id)[:20]

    return ManagerDashboardRead(
        scenario_id=scenario_id,
        delivery=build_delivery_summary(orders),
        delay=build_delay_summary(operations),
        production_progress=build_production_progress(operations),
        capacity=build_capacity_summary(machines, operators),
        bottleneck=build_bottlenecks(operations),
        material_shortage=build_material_shortage_summary(session, inventory_states),
        ncr_rework=build_ncr_rework_summary(ncrs, rework_orders),
        optimizer_performance=build_optimizer_performance(latest_run, schedule_operations),
        risk=risks,
    )


def scoped(session: Session, model: type, scenario_id: int | None) -> list:
    statement = select(model)
    if scenario_id is not None and hasattr(model, "scenario_id"):
        statement = statement.where(model.scenario_id == scenario_id)
    return list(session.exec(statement).all())


def build_delivery_summary(orders: list[CurrentOrderState]) -> DeliverySummary:
    completed = sum(1 for order in orders if order.status in {"Completed", "Finished", "Delivered"})
    delayed = sum(1 for order in orders if is_delayed(order))
    total = len(orders)
    on_time = total - delayed
    return DeliverySummary(
        total_orders=total,
        completed_orders=completed,
        delayed_orders=delayed,
        on_time_rate_percent=round((on_time / total) * 100, 2) if total else 0,
    )


def build_delay_summary(operations: list[CurrentOperationState]) -> DelaySummary:
    return DelaySummary(
        delayed_operations=sum(1 for operation in operations if is_delayed(operation)),
        waiting_material_operations=count_status(operations, {"WaitingMaterial"}),
        waiting_machine_operations=count_status(operations, {"WaitingMachine"}),
        waiting_qc_operations=count_status(operations, {"BlockedByNCR", "WaitingQCApproval"}),
    )


def build_production_progress(operations: list[CurrentOperationState]) -> ProductionProgressSummary:
    finished = count_status(operations, {"Finished", "Completed"})
    active = count_status(operations, {"Running", "InProgress", "Processing"})
    queued = count_status(operations, {"Queued", "WaitingMaterial", "WaitingMachine", "WaitingOperator", "WaitingQCApproval"})
    total = len(operations)
    return ProductionProgressSummary(
        total_operations=total,
        finished_operations=finished,
        active_operations=active,
        queued_operations=queued,
        completion_percent=round((finished / total) * 100, 2) if total else 0,
    )


def build_capacity_summary(machines: list[CurrentMachineState], operators: list[CurrentOperatorState]) -> CapacitySummary:
    busy_machines = count_status(machines, {"Busy", "Running", "Processing"})
    unavailable_machines = count_status(machines, {"Failure", "MaintenanceUnplanned", "MaintenancePlanned", "Offline", "Blocked"})
    busy_operators = count_status(operators, {"Busy", "Running", "Processing"})
    return CapacitySummary(
        total_machines=len(machines),
        busy_machines=busy_machines,
        unavailable_machines=unavailable_machines,
        machine_utilization_percent=round((busy_machines / len(machines)) * 100, 2) if machines else 0,
        total_operators=len(operators),
        busy_operators=busy_operators,
        operator_utilization_percent=round((busy_operators / len(operators)) * 100, 2) if operators else 0,
    )


def build_bottlenecks(operations: list[CurrentOperationState]) -> list[BottleneckItem]:
    queue_by_resource = Counter(
        operation.machine_id or "Unassigned"
        for operation in operations
        if operation.status in {"Queued", "WaitingMachine"} and operation.machine_id is not None
    )
    return [
        BottleneckItem(resource_id=resource_id, queued_operations=count)
        for resource_id, count in queue_by_resource.most_common(5)
    ]


def build_material_shortage_summary(session: Session, inventory_states: list[CurrentInventoryState]) -> MaterialShortageSummary:
    shortage_states = [state for state in inventory_states if state.status == "Shortage"]
    reserved_states = [state for state in inventory_states if state.status == "Reserved"]
    open_requests = session.exec(select(PurchaseRequest).where(PurchaseRequest.status.in_(["Draft", "Approved", "Ordered"]))).all()
    return MaterialShortageSummary(
        shortage_items=len(shortage_states),
        reserved_items=len(reserved_states),
        open_purchase_requests=len(open_requests),
        top_shortages=[
            {
                "inventory_item_id": state.inventory_item_id,
                "warehouse_id": state.warehouse_id,
                "available_qty": state.on_hand_qty - state.reserved_qty,
                "status": state.status,
            }
            for state in shortage_states[:5]
        ],
    )


def build_ncr_rework_summary(ncrs: list[Ncr], rework_orders: list[ReworkOrder]) -> NcrReworkSummary:
    open_ncrs = [ncr for ncr in ncrs if ncr.status in {"Open", "WaitingApproval", "Rejected"}]
    active_reworks = [order for order in rework_orders if order.status not in {"Closed", "Cancelled", "Completed"}]
    return NcrReworkSummary(
        open_ncrs=len(open_ncrs),
        high_severity_ncrs=sum(1 for ncr in open_ncrs if ncr.severity == "High"),
        active_rework_orders=len(active_reworks),
        estimated_delay_min=sum(ncr.estimated_delay_min for ncr in open_ncrs),
    )


def build_optimizer_performance(
    latest_run: OptimizationRun | None,
    schedule_operations: list[ScheduleOperation],
) -> OptimizerPerformanceSummary:
    return OptimizerPerformanceSummary(
        latest_run_id=latest_run.id if latest_run else None,
        status=latest_run.status if latest_run else None,
        score=latest_run.score if latest_run else None,
        changed_operations_count=latest_run.changed_operations_count if latest_run else 0,
        suggested_operations=count_status(schedule_operations, {"Suggested"}),
        accepted_operations=count_status(schedule_operations, {"Accepted"}),
    )


def latest_optimizer_run(session: Session, scenario_id: int | None) -> OptimizationRun | None:
    statement = select(OptimizationRun).order_by(OptimizationRun.id.desc())
    if scenario_id is not None:
        statement = statement.where(OptimizationRun.scenario_id == scenario_id)
    return session.exec(statement).first()


def optimizer_schedule_operations(session: Session, latest_run: OptimizationRun | None) -> list[ScheduleOperation]:
    if latest_run is None or latest_run.id is None:
        return []
    return list(
        session.exec(
            select(ScheduleOperation).where(ScheduleOperation.optimization_run_id == latest_run.id)
        ).all()
    )


def count_status(items: Iterable, statuses: set[str]) -> int:
    return sum(1 for item in items if item.status in statuses)


def is_delayed(item: CurrentOrderState | CurrentOperationState) -> bool:
    payload = item.payload_json or {}
    due_time = payload.get("due_time")
    if due_time is None or item.simulation_time is None:
        return item.status in {"Delayed", "Late"}
    return item.simulation_time > int(due_time) and item.status not in {"Finished", "Completed", "Delivered"}
