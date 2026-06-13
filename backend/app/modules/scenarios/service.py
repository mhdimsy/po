from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.core.time import utc_now
from app.modules.master_data.models import ImportBatch, Machine, MachineProcess, OrderPart, ProductionOrder, RoutingOperation
from app.modules.resources.models import Operator
from app.modules.resources.schemas import GenerateOperatorsRequest
from app.modules.resources.service import generate_operators
from app.modules.events.models import (
    CurrentInventoryState,
    CurrentMachineState,
    CurrentOperationState,
    CurrentOperatorState,
    CurrentOrderState,
)
from app.modules.events.schemas import EventAppendRequest
from app.modules.events.service import append_event
from app.modules.scenarios.models import Scenario, Snapshot
from app.modules.scenarios.schemas import (
    ScenarioCreateRequest,
    ScenarioForkRequest,
    ScenarioSeedRequest,
    ScenarioSeedResponse,
    ProductTreeNode,
    ProductTreeOperationSummary,
    ProductTreeResponse,
    SnapshotCreateRequest,
)


def create_scenario(session: Session, request: ScenarioCreateRequest) -> Scenario:
    scenario = Scenario(
        name=request.name,
        base_import_batch_id=request.base_import_batch_id,
        status=request.status,
        settings_json=request.settings_json,
        notes=request.notes,
    )
    session.add(scenario)
    session.flush()
    append_event(
        session,
        EventAppendRequest(
            event_type="ScenarioCreated",
            aggregate_type="Scenario",
            aggregate_id=str(scenario.id),
            scenario_id=scenario.id,
            payload_json={
                "name": scenario.name,
                "base_import_batch_id": scenario.base_import_batch_id,
                "status": scenario.status,
            },
            update_current_state=False,
        ),
    )
    session.refresh(scenario)
    return scenario


def fork_scenario(session: Session, source_scenario_id: int, request: ScenarioForkRequest) -> Scenario:
    source = session.get(Scenario, source_scenario_id)
    if source is None:
        raise RuntimeError(f"Scenario {source_scenario_id} was not found.")

    scenario = Scenario(
        name=request.name,
        base_import_batch_id=source.base_import_batch_id,
        parent_scenario_id=source.id,
        base_snapshot_id=request.base_snapshot_id,
        status="Draft",
        settings_json={**(source.settings_json or {}), **request.settings_json},
        notes=request.notes,
    )
    session.add(scenario)
    session.flush()
    append_event(
        session,
        EventAppendRequest(
            event_type="ScenarioForked",
            aggregate_type="Scenario",
            aggregate_id=str(scenario.id),
            scenario_id=scenario.id,
            payload_json={
                "parent_scenario_id": source.id,
                "base_snapshot_id": request.base_snapshot_id,
                "name": scenario.name,
            },
            update_current_state=False,
        ),
    )
    session.refresh(scenario)
    return scenario


def create_snapshot(session: Session, scenario_id: int, request: SnapshotCreateRequest) -> Snapshot:
    scenario = session.get(Scenario, scenario_id)
    if scenario is None:
        raise RuntimeError(f"Scenario {scenario_id} was not found.")

    state_json = collect_current_state(session, scenario_id)
    snapshot = Snapshot(
        scenario_id=scenario_id,
        snapshot_time=request.snapshot_time,
        reason=request.reason,
        metadata_json={
            **request.metadata_json,
            "scenario_name": scenario.name,
            "current_state_counts": {
                key: len(value)
                for key, value in state_json.items()
            },
        },
        state_json=state_json,
    )
    session.add(snapshot)
    session.flush()
    append_event(
        session,
        EventAppendRequest(
            event_type="SnapshotCreated",
            aggregate_type="Snapshot",
            aggregate_id=str(snapshot.id),
            scenario_id=scenario_id,
            payload_json={
                "snapshot_id": snapshot.id,
                "reason": snapshot.reason,
                "snapshot_time": snapshot.snapshot_time,
            },
            simulation_time=snapshot.snapshot_time,
            update_current_state=False,
        ),
    )
    session.refresh(snapshot)
    return snapshot


def seed_scenario_from_master_data(session: Session, scenario_id: int, request: ScenarioSeedRequest) -> ScenarioSeedResponse:
    scenario = session.get(Scenario, scenario_id)
    if scenario is None:
        raise RuntimeError(f"Scenario {scenario_id} was not found.")

    import_batch_id = request.import_batch_id or scenario.base_import_batch_id or latest_import_batch_id(session)
    if import_batch_id is None:
        raise RuntimeError("No ImportBatch was found. Import master data before seeding a scenario.")

    if request.reset_existing_state:
        clear_scenario_current_state(session, scenario_id)

    machines = list(
        session.exec(
            select(Machine)
            .where(Machine.import_batch_id == import_batch_id)
            .order_by(Machine.id)
        ).all()
    )
    machine_processes = list(
        session.exec(
            select(MachineProcess)
            .where(MachineProcess.import_batch_id == import_batch_id)
            .order_by(MachineProcess.id)
        ).all()
    )
    machines_by_process: dict[int, list[Machine]] = {}
    machine_by_source_id = {machine.source_machine_id: machine for machine in machines}
    for capability in machine_processes:
        machine = machine_by_source_id.get(capability.machine_id)
        if machine is not None:
            machines_by_process.setdefault(capability.process_id, []).append(machine)

    operators = ensure_seed_operators(session, len(machines))
    operator_pools = build_operator_pools(operators)
    operator_cursor_by_work_center: dict[int | None, int] = {}

    for operator in operators:
        session.add(
            CurrentOperatorState(
                scenario_id=scenario_id,
                operator_id=operator.code,
                status=operator.status or "Available",
                payload_json={
                    "operator_db_id": operator.id,
                    "full_name": operator.full_name,
                    "home_work_center_id": operator.home_work_center_id,
                    "primary_shift_id": operator.primary_shift_id,
                    "source": "master_data_seed",
                },
            )
        )

    for machine in machines:
        session.add(
            CurrentMachineState(
                scenario_id=scenario_id,
                machine_id=str(machine.source_machine_id),
                status=machine.status or "Available",
                payload_json={
                    "title": machine.title,
                    "barcode": machine.barcode,
                    "work_center_id": machine.work_center_id,
                    "source": "master_data_seed",
                },
            )
        )

    orders = list(
        session.exec(
            select(ProductionOrder)
            .where(ProductionOrder.import_batch_id == import_batch_id)
            .order_by(ProductionOrder.id)
            .limit(request.max_orders)
        ).all()
    )
    routing_ids = {order.routine_id for order in orders if order.routine_id is not None}
    routing_operations = list(
        session.exec(
            select(RoutingOperation)
            .where(RoutingOperation.import_batch_id == import_batch_id)
            .where(RoutingOperation.routine_id.in_(routing_ids))
            .order_by(RoutingOperation.routine_id, RoutingOperation.operation_sequence, RoutingOperation.id)
        ).all()
    ) if routing_ids else []
    operations_by_routing: dict[int, list[RoutingOperation]] = {}
    for operation in routing_operations:
        operations_by_routing.setdefault(operation.routine_id, []).append(operation)

    operations_seeded = 0
    skipped_orders_without_routing = 0
    for index, order in enumerate(orders):
        due_time = due_time_minutes(order, fallback=(index + 1) * 1440)
        session.add(
            CurrentOrderState(
                scenario_id=scenario_id,
                order_id=str(order.source_order_id),
                status="Created",
                payload_json={
                    "code": order.code,
                    "routine_id": order.routine_id,
                    "bom_id": order.bom_id,
                    "product_code": order.product_code,
                    "customer_name": order.customer_name,
                    "due_time": due_time,
                    "source": "master_data_seed",
                },
            )
        )

        order_operations = operations_by_routing.get(order.routine_id or -1, [])
        if not order_operations:
            skipped_orders_without_routing += 1
            continue

        for operation in order_operations:
            machine = choose_seed_machine(operation.process_id, machines_by_process)
            operator = choose_seed_operator(machine.work_center_id if machine else None, operator_pools, operator_cursor_by_work_center)
            duration = operation_duration_minutes(operation)
            session.add(
                CurrentOperationState(
                    scenario_id=scenario_id,
                    operation_id=f"{order.source_order_id}-{operation.source_routine_operation_id}",
                    order_id=str(order.source_order_id),
                    machine_id=str(machine.source_machine_id) if machine else None,
                    operator_id=operator.code if operator else None,
                    status="Queued",
                    simulation_time=0,
                    payload_json={
                        "order_id": str(order.source_order_id),
                        "order_code": order.code,
                        "routine_id": operation.routine_id,
                        "routing_operation_id": operation.source_routine_operation_id,
                        "process_id": operation.process_id,
                        "operation_sequence": operation.operation_sequence,
                        "operation_description": operation.operation_description,
                        "duration": duration,
                        "operation_duration": duration,
                        "due_time": due_time,
                        "priority": 1,
                        "machine_id": str(machine.source_machine_id) if machine else None,
                        "operator_id": operator.code if operator else None,
                        "work_center_id": machine.work_center_id if machine else None,
                        "source": "master_data_seed",
                    },
                )
            )
            operations_seeded += 1

    scenario.status = "Seeded"
    scenario.base_import_batch_id = import_batch_id
    scenario.settings_json = {
        **(scenario.settings_json or {}),
        "seed": {
            "import_batch_id": import_batch_id,
            "max_orders": request.max_orders,
            "orders_seeded": len(orders),
            "operations_seeded": operations_seeded,
            "machines_seeded": len(machines),
            "seeded_at": utc_now().isoformat(),
        },
    }
    session.add(scenario)
    session.flush()
    append_event(
        session,
        EventAppendRequest(
            event_type="ScenarioSeededFromMasterData",
            aggregate_type="Scenario",
            aggregate_id=str(scenario.id),
            scenario_id=scenario.id,
            payload_json=scenario.settings_json["seed"],
            update_current_state=False,
        ),
    )
    return ScenarioSeedResponse(
        scenario_id=scenario_id,
        import_batch_id=import_batch_id,
        orders_seeded=len(orders),
        operations_seeded=operations_seeded,
        machines_seeded=len(machines),
        skipped_orders_without_routing=skipped_orders_without_routing,
        max_orders=request.max_orders,
    )


def latest_import_batch_id(session: Session) -> int | None:
    batch = session.exec(select(ImportBatch).order_by(ImportBatch.id.desc())).first()
    return batch.id if batch else None


def clear_scenario_current_state(session: Session, scenario_id: int) -> None:
    for model in (CurrentOrderState, CurrentOperationState, CurrentMachineState, CurrentOperatorState, CurrentInventoryState):
        for row in session.exec(select(model).where(model.scenario_id == scenario_id)).all():
            session.delete(row)
    session.flush()


def choose_seed_machine(process_id: int, machines_by_process: dict[int, list[Machine]]) -> Machine | None:
    candidates = machines_by_process.get(process_id) or []
    return candidates[0] if candidates else None


def ensure_seed_operators(session: Session, machine_count: int) -> list[Operator]:
    operators = list(session.exec(select(Operator).order_by(Operator.id)).all())
    if operators:
        return operators
    generate_operators(
        session,
        GenerateOperatorsRequest(
            count=max(50, min(1000, machine_count * 2)),
            seed=42,
        ),
    )
    return list(session.exec(select(Operator).order_by(Operator.id)).all())


def build_operator_pools(operators: list[Operator]) -> dict[int | None, list[Operator]]:
    pools: dict[int | None, list[Operator]] = {}
    for operator in operators:
        pools.setdefault(operator.home_work_center_id, []).append(operator)
        pools.setdefault(None, []).append(operator)
    return pools


def choose_seed_operator(
    work_center_id: int | None,
    operator_pools: dict[int | None, list[Operator]],
    cursor_by_work_center: dict[int | None, int],
) -> Operator | None:
    pool = operator_pools.get(work_center_id) or operator_pools.get(None) or []
    if not pool:
        return None
    key = work_center_id if work_center_id in operator_pools else None
    cursor = cursor_by_work_center.get(key, 0)
    operator = pool[cursor % len(pool)]
    cursor_by_work_center[key] = cursor + 1
    return operator


def operation_duration_minutes(operation: RoutingOperation) -> int:
    values = [
        operation.setup_duration or 0,
        operation.operation_duration or 0,
        operation.assembly_duration or 0,
        operation.outsource_lead_time_minutes or 0,
    ]
    return max(1, sum(value for value in values if value > 0))


def get_product_tree(
    session: Session,
    scenario_id: int,
    root_order_id: str | None = None,
    root_limit: int = 25,
    max_depth: int = 6,
) -> ProductTreeResponse:
    scenario = session.get(Scenario, scenario_id)
    if scenario is None:
        raise RuntimeError(f"Scenario {scenario_id} was not found.")

    current_orders = list(session.exec(select(CurrentOrderState).where(CurrentOrderState.scenario_id == scenario_id)).all())
    current_operations = list(session.exec(select(CurrentOperationState).where(CurrentOperationState.scenario_id == scenario_id)).all())
    order_by_id = {order.order_id: order for order in current_orders}
    operations_by_order: dict[str, list[CurrentOperationState]] = {}
    for operation in current_operations:
        if operation.order_id is not None:
            operations_by_order.setdefault(operation.order_id, []).append(operation)

    import_batch_id = scenario.base_import_batch_id or latest_import_batch_id(session)
    order_parts = []
    if import_batch_id is not None:
        order_parts = list(
            session.exec(
                select(OrderPart)
                .where(OrderPart.import_batch_id == import_batch_id)
                .order_by(OrderPart.parent_order_id, OrderPart.child_order_id)
            ).all()
        )

    current_order_ids = set(order_by_id)
    master_orders_by_id: dict[str, ProductionOrder] = {}
    master_order_ids: set[str] = set()
    if import_batch_id is not None:
        master_orders = list(
            session.exec(
                select(ProductionOrder)
                .where(ProductionOrder.import_batch_id == import_batch_id)
            ).all()
        )
        master_orders_by_id = {str(order.source_order_id): order for order in master_orders}
        master_order_ids = set(master_orders_by_id)

    scoped_order_ids = current_order_ids | master_order_ids
    children_by_parent: dict[str, list[tuple[str, str | None]]] = {}
    child_ids: set[str] = set()
    for part in order_parts:
        parent_id = str(part.parent_order_id)
        child_id = str(part.child_order_id)
        if parent_id not in scoped_order_ids or child_id not in scoped_order_ids:
            continue
        children_by_parent.setdefault(parent_id, []).append((child_id, part.assignment_status_title))
        child_ids.add(child_id)

    if root_order_id is not None:
        root_ids = [root_order_id] if root_order_id in scoped_order_ids else []
    else:
        root_ids = [order_id for order_id in current_order_ids if order_id not in child_ids]
        root_ids.sort(key=order_id_sort_key)
        root_ids = root_ids[:root_limit]

    roots = [
        build_product_tree_node(
            order_id,
            order_by_id,
            master_orders_by_id,
            operations_by_order,
            children_by_parent,
            max_depth,
            assignment_status=None,
            depth=0,
            visited=set(),
        )
        for order_id in root_ids
    ]
    return ProductTreeResponse(
        scenario_id=scenario_id,
        root_count=len(roots),
        total_orders_in_scope=len(current_order_ids),
        max_depth=max_depth,
        roots=roots,
    )


def build_product_tree_node(
    order_id: str,
    order_by_id: dict[str, CurrentOrderState],
    master_orders_by_id: dict[str, ProductionOrder],
    operations_by_order: dict[str, list[CurrentOperationState]],
    children_by_parent: dict[str, list[tuple[str, str | None]]],
    max_depth: int,
    assignment_status: str | None,
    depth: int,
    visited: set[str],
) -> ProductTreeNode:
    order = order_by_id.get(order_id)
    master_order = master_orders_by_id.get(order_id)
    operations = operations_by_order.get(order_id, [])
    summary = summarize_operations(operations)
    status = order.status if order is not None else "NotSeeded"
    computed_status = compute_order_status(status, summary)
    children: list[ProductTreeNode] = []
    if depth < max_depth and order_id not in visited:
        next_visited = {*visited, order_id}
        for child_id, child_assignment_status in children_by_parent.get(order_id, []):
            if child_id in order_by_id or child_id in master_orders_by_id:
                children.append(
                    build_product_tree_node(
                        child_id,
                        order_by_id,
                        master_orders_by_id,
                        operations_by_order,
                        children_by_parent,
                        max_depth,
                        child_assignment_status,
                        depth + 1,
                        next_visited,
                    )
                )
    payload = order.payload_json if order is not None else {}
    return ProductTreeNode(
        order_id=order_id,
        order_code=string_or_none(payload.get("code")) or (master_order.code if master_order is not None else None),
        product_code=string_or_none(payload.get("product_code")) or (master_order.product_code if master_order is not None else None),
        status=status,
        computed_status=computed_status,
        assignment_status=assignment_status,
        operation_summary=summary,
        children=children,
    )


def summarize_operations(operations: list[CurrentOperationState]) -> ProductTreeOperationSummary:
    queued = sum(1 for operation in operations if operation.status in {"Queued", "WaitingMaterial", "WaitingMachine", "WaitingOperator", "WaitingQCApproval"})
    setup = sum(1 for operation in operations if operation.status == "Setup")
    running = sum(1 for operation in operations if operation.status in {"Running", "QC", "Rework"})
    finished = sum(1 for operation in operations if operation.status in {"Finished", "Completed"})
    blocked = sum(1 for operation in operations if operation.status in {"Blocked", "BlockedByNCR", "WaitingMaterial", "WaitingMachine"})
    total = len(operations)
    known = queued + setup + running + finished + blocked
    return ProductTreeOperationSummary(total=total, queued=queued, setup=setup, running=running, finished=finished, blocked=blocked, other=max(0, total - known))


def compute_order_status(order_status: str, summary: ProductTreeOperationSummary) -> str:
    if summary.total == 0:
        return order_status
    if summary.finished >= summary.total:
        return "Finished"
    if summary.running > 0 or summary.setup > 0:
        return "Running"
    if summary.blocked > 0:
        return "Blocked"
    if summary.queued > 0:
        return "Queued"
    return order_status


def order_id_sort_key(value: str) -> tuple[int, int | str]:
    return (0, int(value)) if value.isdigit() else (1, value)


def string_or_none(value) -> str | None:
    if value is None:
        return None
    return str(value)


def due_time_minutes(order: ProductionOrder, fallback: int) -> int:
    due_date = (
        order.internal_production_due_date
        or order.committed_delivery_date
        or order.customer_requested_date
        or order.material_required_date
        or order.shipment_date
    )
    if due_date is None:
        return fallback
    reference = order.order_date or due_date
    return max(1, int((due_date - reference).total_seconds() // 60))


def collect_current_state(session: Session, scenario_id: int) -> dict[str, list[dict[str, Any]]]:
    return {
        "orders": dump_rows(session.exec(select(CurrentOrderState).where(CurrentOrderState.scenario_id == scenario_id)).all()),
        "operations": dump_rows(session.exec(select(CurrentOperationState).where(CurrentOperationState.scenario_id == scenario_id)).all()),
        "machines": dump_rows(session.exec(select(CurrentMachineState).where(CurrentMachineState.scenario_id == scenario_id)).all()),
        "operators": dump_rows(session.exec(select(CurrentOperatorState).where(CurrentOperatorState.scenario_id == scenario_id)).all()),
        "inventory": dump_rows(session.exec(select(CurrentInventoryState).where(CurrentInventoryState.scenario_id == scenario_id)).all()),
    }


def dump_rows(rows: list[Any]) -> list[dict[str, Any]]:
    return [json_safe(row.model_dump()) for row in rows]


def json_safe(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    return value
