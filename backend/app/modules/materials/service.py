from __future__ import annotations

import random

from sqlmodel import Session, select

from app.modules.master_data.models import BOM, BOMPart
from app.modules.materials.models import (
    BOMItemSupplier,
    InventoryBalance,
    InventoryItem,
    PurchaseRequest,
    Supplier,
    Warehouse,
)
from app.modules.materials.schemas import (
    GenerateInventoryRequest,
    GenerateInventoryResponse,
    GenerateSuppliersRequest,
    GenerateSuppliersResponse,
)


INVENTORY_PRESETS = {
    "Plenty": (200, 500),
    "Normal": (50, 180),
    "Shortage-heavy": (0, 40),
    "Random Chaos": (0, 600),
}

SUPPLIER_PRESETS = {
    "Reliable": {"reliability": (0.88, 0.99), "lead_time": (3, 10)},
    "Mixed": {"reliability": (0.55, 0.98), "lead_time": (4, 24)},
    "Unreliable": {"reliability": (0.35, 0.75), "lead_time": (14, 45)},
    "Fast but Expensive": {"reliability": (0.70, 0.95), "lead_time": (1, 5)},
}


def generate_inventory(session: Session, request: GenerateInventoryRequest) -> GenerateInventoryResponse:
    rng = random.Random(request.seed)
    preset = normalize_inventory_preset(request.preset)
    warehouse = ensure_warehouse(session, request.warehouse_code, request.warehouse_title)
    bom_items = session.exec(select(BOM)).all()

    items_created = 0
    balances_created = 0
    purchase_requests_created = 0
    total_on_hand = 0.0

    for bom in bom_items:
        item = ensure_inventory_item(session, bom)
        if item.id is None:
            session.flush()
        items_created += 1

        on_hand_qty = generate_on_hand_qty(rng, preset)
        safety_stock_qty = calculate_safety_stock(session, bom.source_bom_id, request.safety_stock_percent)
        balance = InventoryBalance(
            inventory_item_id=item.id,
            warehouse_id=warehouse.id,
            on_hand_qty=on_hand_qty,
            reserved_qty=0,
            safety_stock_qty=safety_stock_qty,
            preset=preset,
        )
        session.add(balance)
        balances_created += 1
        total_on_hand += on_hand_qty

        if request.create_purchase_requests and on_hand_qty < safety_stock_qty:
            shortage_qty = safety_stock_qty - on_hand_qty
            session.add(
                PurchaseRequest(
                    inventory_item_id=item.id,
                    supplier_id=None,
                    shortage_qty=shortage_qty,
                    suggested_qty=shortage_qty * (1 + request.safety_stock_percent),
                    final_qty=None,
                    status="Draft",
                )
            )
            purchase_requests_created += 1

    session.commit()
    return GenerateInventoryResponse(
        preset=preset,
        warehouse_id=warehouse.id,
        inventory_items_created=items_created,
        inventory_balances_created=balances_created,
        purchase_requests_created=purchase_requests_created,
        total_on_hand_qty=total_on_hand,
    )


def generate_suppliers(session: Session, request: GenerateSuppliersRequest) -> GenerateSuppliersResponse:
    rng = random.Random(request.seed)
    preset = normalize_supplier_preset(request.preset)
    inventory_items = session.exec(select(InventoryItem)).all()
    if not inventory_items:
        for bom in session.exec(select(BOM)).all():
            ensure_inventory_item(session, bom)
        session.flush()
        inventory_items = session.exec(select(InventoryItem)).all()

    supplier_count = max(request.suppliers_per_item, min(4, request.suppliers_per_item))
    suppliers = ensure_suppliers(session, preset, supplier_count, rng)
    mappings_created = 0
    default_mappings_created = 0

    for item in inventory_items:
        default_supplier = rng.choice(suppliers)
        for supplier in rng.sample(suppliers, min(request.suppliers_per_item, len(suppliers))):
            existing = session.exec(
                select(BOMItemSupplier).where(
                    BOMItemSupplier.inventory_item_id == item.id,
                    BOMItemSupplier.supplier_id == supplier.id,
                )
            ).first()
            if existing is not None:
                continue
            is_default = supplier.id == default_supplier.id
            session.add(
                BOMItemSupplier(
                    inventory_item_id=item.id,
                    supplier_id=supplier.id,
                    is_default=is_default,
                )
            )
            mappings_created += 1
            if is_default:
                default_mappings_created += 1

    session.commit()
    return GenerateSuppliersResponse(
        preset=preset,
        suppliers_created=len(suppliers),
        mappings_created=mappings_created,
        default_mappings_created=default_mappings_created,
    )


def ensure_warehouse(session: Session, code: str, title: str) -> Warehouse:
    warehouse = session.exec(select(Warehouse).where(Warehouse.code == code)).first()
    if warehouse is None:
        warehouse = Warehouse(code=code, title=title)
        session.add(warehouse)
        session.flush()
    return warehouse


def ensure_inventory_item(session: Session, bom: BOM) -> InventoryItem:
    code = bom.code or f"BOM-{bom.source_bom_id}"
    item = session.exec(select(InventoryItem).where(InventoryItem.bom_id == bom.source_bom_id)).first()
    if item is None:
        item = InventoryItem(
            bom_id=bom.source_bom_id,
            code=code,
            title=bom.title or code,
            unit="EA",
        )
        session.add(item)
        session.flush()
    return item


def ensure_suppliers(
    session: Session,
    preset: str,
    supplier_count: int,
    rng: random.Random,
) -> list[Supplier]:
    suppliers: list[Supplier] = []
    profile = SUPPLIER_PRESETS[preset]
    for index in range(1, supplier_count + 1):
        code = f"{preset.upper().replace(' ', '-')}-SUP-{index:02d}"
        supplier = session.exec(select(Supplier).where(Supplier.code == code)).first()
        if supplier is None:
            lead_time_days = rng.randint(*profile["lead_time"])
            supplier = Supplier(
                code=code,
                title=f"{preset} Supplier {index:02d}",
                preset_type=preset,
                reliability_score=round(rng.uniform(*profile["reliability"]), 3),
                default_lead_time_min=lead_time_days * 24 * 60,
            )
            session.add(supplier)
            session.flush()
        suppliers.append(supplier)
    return suppliers


def generate_on_hand_qty(rng: random.Random, preset: str) -> float:
    low, high = INVENTORY_PRESETS[preset]
    return float(rng.randint(low, high))


def calculate_safety_stock(session: Session, bom_id: int, safety_stock_percent: float) -> float:
    children = session.exec(select(BOMPart).where(BOMPart.bom_parent_id == bom_id)).all()
    if not children:
        return 20 * (1 + safety_stock_percent)
    required_qty = sum(max(0, child.quantity) for child in children)
    return max(1, required_qty * 10 * (1 + safety_stock_percent))


def normalize_inventory_preset(preset: str) -> str:
    normalized = preset.strip()
    if normalized not in INVENTORY_PRESETS:
        return "Normal"
    return normalized


def normalize_supplier_preset(preset: str) -> str:
    normalized = preset.strip()
    if normalized == "Reliable Suppliers":
        return "Reliable"
    if normalized == "Mixed Suppliers":
        return "Mixed"
    if normalized == "Unreliable Suppliers":
        return "Unreliable"
    if normalized not in SUPPLIER_PRESETS:
        return "Mixed"
    return normalized
