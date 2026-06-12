from __future__ import annotations

from sqlmodel import Session, select

from app.core.time import utc_now
from app.modules.events.models import CurrentInventoryState, CurrentMachineState, CurrentOperationState, CurrentOrderState
from app.modules.optimizer.models import OptimizationRun
from app.modules.qc_ncr.models import Ncr, ReworkOrder
from app.modules.risk.models import RiskRuleSetting, RiskScore
from app.modules.risk.schemas import RiskCalculationResponse, RiskSettingsRead, RiskSettingsUpdate
from app.modules.scenarios.models import Scenario


DEFAULT_SETTINGS = {
    "delay_risk_weight": 1.0,
    "material_shortage_risk_weight": 1.0,
    "machine_failure_risk_weight": 1.0,
    "qc_ncr_risk_weight": 1.0,
    "schedule_instability_weight": 1.0,
    "low_threshold": 30.0,
    "medium_threshold": 60.0,
    "high_threshold": 85.0,
}


def get_risk_settings(session: Session) -> RiskSettingsRead:
    ensure_default_settings(session)
    values = {setting.key: setting.value for setting in session.exec(select(RiskRuleSetting)).all()}
    return RiskSettingsRead(**{key: values.get(key, default) for key, default in DEFAULT_SETTINGS.items()})


def update_risk_settings(session: Session, request: RiskSettingsUpdate) -> RiskSettingsRead:
    ensure_default_settings(session)
    updates = request.model_dump(exclude_none=True)
    current = get_risk_settings(session).model_dump()
    proposed = {**current, **updates}
    validate_thresholds(proposed)
    for key, value in updates.items():
        setting = session.exec(select(RiskRuleSetting).where(RiskRuleSetting.key == key)).first()
        if setting is None:
            setting = RiskRuleSetting(key=key, value=float(value))
        else:
            setting.value = float(value)
            setting.updated_at = utc_now()
        session.add(setting)
    session.commit()
    return get_risk_settings(session)


def calculate_risk_scores(session: Session, scenario_id: int) -> RiskCalculationResponse:
    if session.get(Scenario, scenario_id) is None:
        raise RuntimeError(f"Scenario {scenario_id} was not found.")

    settings = get_risk_settings(session)
    existing_scores = session.exec(select(RiskScore).where(RiskScore.scenario_id == scenario_id)).all()
    for score in existing_scores:
        session.delete(score)
    session.flush()

    scores: list[RiskScore] = []
    operations = session.exec(select(CurrentOperationState).where(CurrentOperationState.scenario_id == scenario_id)).all()
    orders = session.exec(select(CurrentOrderState).where(CurrentOrderState.scenario_id == scenario_id)).all()

    for operation in operations:
        scores.append(create_operation_risk(session, scenario_id, operation, settings))
    for order in orders:
        scores.append(create_order_risk(session, scenario_id, order, operations, settings))

    scenario_score = create_scenario_risk(session, scenario_id, scores, settings)
    session.commit()
    session.refresh(scenario_score)
    for score in scores:
        session.refresh(score)
    return RiskCalculationResponse(
        scenario_id=scenario_id,
        scores_created=len(scores) + 1,
        scenario_risk=scenario_score,
        scores=scores,
    )


def list_risk_scores(session: Session, scenario_id: int | None = None) -> list[RiskScore]:
    statement = select(RiskScore).order_by(RiskScore.total_score.desc())
    if scenario_id is not None:
        statement = statement.where(RiskScore.scenario_id == scenario_id)
    return list(session.exec(statement).all())


def create_operation_risk(session: Session, scenario_id: int, operation: CurrentOperationState, settings: RiskSettingsRead) -> RiskScore:
    payload = operation.payload_json or {}
    delay = 0.0
    due_time = payload.get("due_time")
    if due_time is not None and operation.simulation_time is not None:
        delay = min(100, max(0, operation.simulation_time - int(due_time)))
    if operation.status in {"Queued", "WaitingMaterial", "WaitingMachine", "WaitingOperator", "BlockedByNCR", "WaitingQCApproval"}:
        delay += 15

    material = 0.0
    if operation.status == "WaitingMaterial" or payload.get("blocked_reason") == "material_unavailable":
        material = 80
    required_inventory = payload.get("required_inventory_item_id")
    required_qty = float(payload.get("required_qty") or 0)
    if required_inventory and required_qty > 0:
        inventory = session.exec(
            select(CurrentInventoryState)
            .where(CurrentInventoryState.scenario_id == scenario_id)
            .where(CurrentInventoryState.inventory_item_id == str(required_inventory))
        ).first()
        if inventory is None or inventory.on_hand_qty - inventory.reserved_qty < required_qty:
            material = max(material, 90)

    machine = 0.0
    if operation.machine_id:
        machine_state = session.exec(
            select(CurrentMachineState)
            .where(CurrentMachineState.scenario_id == scenario_id)
            .where(CurrentMachineState.machine_id == operation.machine_id)
        ).first()
        if machine_state and machine_state.status in {"Failure", "MaintenanceUnplanned", "Offline"}:
            machine = 90
        elif machine_state and machine_state.status in {"MaintenancePlanned", "Repairing", "Blocked"}:
            machine = 60

    qc_ncr = 0.0
    if operation.status in {"BlockedByNCR", "WaitingQCApproval", "Rework", "Scrap"}:
        qc_ncr = 85

    instability = latest_instability(session, scenario_id)
    components = weighted_components(delay, material, machine, qc_ncr, instability, settings)
    return persist_score(session, scenario_id, "Operation", operation.operation_id, components, settings)


def create_order_risk(
    session: Session,
    scenario_id: int,
    order: CurrentOrderState,
    operations: list[CurrentOperationState],
    settings: RiskSettingsRead,
) -> RiskScore:
    order_operations = [operation for operation in operations if operation.order_id == order.order_id]
    unfinished = [operation for operation in order_operations if operation.status not in {"Finished"}]
    blocked = [operation for operation in order_operations if operation.status in {"Blocked", "BlockedByNCR", "WaitingMaterial", "WaitingQCApproval"}]
    delay = min(100, len(unfinished) * 12)
    material = 80 if any(operation.status == "WaitingMaterial" for operation in blocked) else 0
    machine = 50 if any(operation.status == "WaitingMachine" for operation in blocked) else 0
    qc_ncr = 85 if any(operation.status in {"BlockedByNCR", "WaitingQCApproval", "Rework"} for operation in blocked) else 0
    instability = latest_instability(session, scenario_id)
    components = weighted_components(delay, material, machine, qc_ncr, instability, settings)
    return persist_score(session, scenario_id, "Order", order.order_id, components, settings)


def create_scenario_risk(session: Session, scenario_id: int, child_scores: list[RiskScore], settings: RiskSettingsRead) -> RiskScore:
    open_ncrs = len(session.exec(select(Ncr).where(Ncr.scenario_id == scenario_id).where(Ncr.status.in_(["Open", "WaitingApproval", "Rejected"]))).all())
    reworks = len(session.exec(select(ReworkOrder).where(ReworkOrder.scenario_id == scenario_id)).all())
    failed_machines = len(session.exec(select(CurrentMachineState).where(CurrentMachineState.scenario_id == scenario_id).where(CurrentMachineState.status.in_(["Failure", "MaintenanceUnplanned", "Offline"]))).all())
    material_shortages = len(session.exec(select(CurrentInventoryState).where(CurrentInventoryState.scenario_id == scenario_id).where(CurrentInventoryState.status.in_(["Shortage", "Reserved"]))).all())
    average_child_score = sum(score.total_score for score in child_scores) / len(child_scores) if child_scores else 0
    components = weighted_components(
        delay=average_child_score,
        material=min(100, material_shortages * 20),
        machine=min(100, failed_machines * 35),
        qc_ncr=min(100, open_ncrs * 35 + reworks * 20),
        instability=latest_instability(session, scenario_id),
        settings=settings,
    )
    return persist_score(session, scenario_id, "Scenario", str(scenario_id), components, settings)


def latest_instability(session: Session, scenario_id: int) -> float:
    latest_run = session.exec(
        select(OptimizationRun)
        .where(OptimizationRun.scenario_id == scenario_id)
        .order_by(OptimizationRun.id.desc())
    ).first()
    if latest_run is None:
        return 0
    return min(100, latest_run.changed_operations_count * 10)


def weighted_components(delay: float, material: float, machine: float, qc_ncr: float, instability: float, settings: RiskSettingsRead) -> dict:
    return {
        "delay": delay * settings.delay_risk_weight,
        "material_shortage": material * settings.material_shortage_risk_weight,
        "machine_failure": machine * settings.machine_failure_risk_weight,
        "qc_ncr": qc_ncr * settings.qc_ncr_risk_weight,
        "schedule_instability": instability * settings.schedule_instability_weight,
    }


def persist_score(session: Session, scenario_id: int, aggregate_type: str, aggregate_id: str, components: dict, settings: RiskSettingsRead) -> RiskScore:
    total = round(min(100, sum(components.values()) / max(1, len(components))), 2)
    score = RiskScore(
        scenario_id=scenario_id,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        total_score=total,
        level=risk_level(total, settings),
        components_json=components,
    )
    session.add(score)
    session.flush()
    return score


def risk_level(total_score: float, settings: RiskSettingsRead) -> str:
    if total_score >= settings.high_threshold:
        return "High"
    if total_score >= settings.medium_threshold:
        return "Medium"
    return "Low"


def validate_thresholds(values: dict) -> None:
    low = float(values["low_threshold"])
    medium = float(values["medium_threshold"])
    high = float(values["high_threshold"])
    if not low <= medium <= high:
        raise RuntimeError("Risk thresholds must be ordered as low_threshold <= medium_threshold <= high_threshold.")


def ensure_default_settings(session: Session) -> None:
    existing_keys = {setting.key for setting in session.exec(select(RiskRuleSetting)).all()}
    changed = False
    for key, value in DEFAULT_SETTINGS.items():
        if key not in existing_keys:
            session.add(RiskRuleSetting(key=key, value=value))
            changed = True
    if changed:
        session.commit()
