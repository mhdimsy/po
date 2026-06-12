from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.core.db import get_session
from app.modules.materials.models import (
    BOMItemSupplier,
    InventoryBalance,
    InventoryItem,
    PurchaseRequest,
    Supplier,
)
from app.modules.materials.schemas import (
    BOMItemSupplierRead,
    GenerateInventoryRequest,
    GenerateInventoryResponse,
    GenerateSuppliersRequest,
    GenerateSuppliersResponse,
    InventoryBalanceRead,
    InventoryItemRead,
    PurchaseRequestRead,
    SupplierRead,
)
from app.modules.materials.service import generate_inventory, generate_suppliers

router = APIRouter(tags=["synthetic-materials"])


@router.post("/inventory/generate", response_model=GenerateInventoryResponse)
def generate_synthetic_inventory(
    request: GenerateInventoryRequest | None = None,
    session: Session = Depends(get_session),
):
    return generate_inventory(session, request or GenerateInventoryRequest())


@router.post("/suppliers/generate", response_model=GenerateSuppliersResponse)
def generate_synthetic_suppliers(
    request: GenerateSuppliersRequest | None = None,
    session: Session = Depends(get_session),
):
    return generate_suppliers(session, request or GenerateSuppliersRequest())


@router.get("/inventory-items", response_model=list[InventoryItemRead])
def list_inventory_items(session: Session = Depends(get_session), limit: int = Query(100, le=1000)):
    return list(session.exec(select(InventoryItem).limit(limit)).all())


@router.get("/inventory-balances", response_model=list[InventoryBalanceRead])
def list_inventory_balances(session: Session = Depends(get_session), limit: int = Query(100, le=1000)):
    return list(session.exec(select(InventoryBalance).limit(limit)).all())


@router.get("/suppliers", response_model=list[SupplierRead])
def list_suppliers(session: Session = Depends(get_session), limit: int = Query(100, le=1000)):
    return list(session.exec(select(Supplier).limit(limit)).all())


@router.get("/bom-item-suppliers", response_model=list[BOMItemSupplierRead])
def list_bom_item_suppliers(session: Session = Depends(get_session), limit: int = Query(100, le=1000)):
    return list(session.exec(select(BOMItemSupplier).limit(limit)).all())


@router.get("/purchase-requests", response_model=list[PurchaseRequestRead])
def list_purchase_requests(session: Session = Depends(get_session), limit: int = Query(100, le=1000)):
    return list(session.exec(select(PurchaseRequest).limit(limit)).all())
