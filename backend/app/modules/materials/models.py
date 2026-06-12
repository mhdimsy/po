from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlmodel import Field, SQLModel

from app.core.time import utc_now


class Warehouse(SQLModel, table=True):
    __tablename__ = "warehouses"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, max_length=80)
    title: str = Field(max_length=255)
    is_synthetic: bool = Field(default=True, sa_column=Column("IsSynthetic", Boolean))


class InventoryItem(SQLModel, table=True):
    __tablename__ = "inventory_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    bom_id: int = Field(sa_column=Column("BOM_Id", Integer, index=True))
    code: str = Field(index=True, max_length=120)
    title: str = Field(max_length=255)
    unit: str = Field(default="EA", max_length=40)
    is_synthetic: bool = Field(default=True, sa_column=Column("IsSynthetic", Boolean))


class InventoryBalance(SQLModel, table=True):
    __tablename__ = "inventory_balances"

    id: Optional[int] = Field(default=None, primary_key=True)
    inventory_item_id: int = Field(foreign_key="inventory_items.id", index=True)
    warehouse_id: int = Field(foreign_key="warehouses.id", index=True)
    on_hand_qty: float = Field(default=0, sa_column=Column("OnHandQty", Float))
    reserved_qty: float = Field(default=0, sa_column=Column("ReservedQty", Float))
    safety_stock_qty: float = Field(default=0, sa_column=Column("SafetyStockQty", Float))
    preset: str = Field(max_length=80)
    generated_at: datetime = Field(default_factory=utc_now, sa_column=Column("GeneratedAt", DateTime))


class Supplier(SQLModel, table=True):
    __tablename__ = "suppliers"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, max_length=80)
    title: str = Field(max_length=255)
    preset_type: str = Field(max_length=80)
    reliability_score: float = Field(default=1, sa_column=Column("ReliabilityScore", Float))
    default_lead_time_min: int = Field(sa_column=Column("DefaultLeadTimeMin", Integer))
    is_synthetic: bool = Field(default=True, sa_column=Column("IsSynthetic", Boolean))


class BOMItemSupplier(SQLModel, table=True):
    __tablename__ = "bom_item_suppliers"

    id: Optional[int] = Field(default=None, primary_key=True)
    inventory_item_id: int = Field(foreign_key="inventory_items.id", index=True)
    supplier_id: int = Field(foreign_key="suppliers.id", index=True)
    is_default: bool = Field(default=False, sa_column=Column("IsDefault", Boolean))
    is_synthetic: bool = Field(default=True, sa_column=Column("IsSynthetic", Boolean))


class PurchaseRequest(SQLModel, table=True):
    __tablename__ = "purchase_requests"

    id: Optional[int] = Field(default=None, primary_key=True)
    inventory_item_id: int = Field(foreign_key="inventory_items.id", index=True)
    supplier_id: Optional[int] = Field(default=None, foreign_key="suppliers.id", index=True)
    shortage_qty: float = Field(sa_column=Column("ShortageQty", Float))
    suggested_qty: float = Field(sa_column=Column("SuggestedQty", Float))
    final_qty: Optional[float] = Field(default=None, sa_column=Column("FinalQty", Float))
    status: str = Field(default="Draft", max_length=80)
    created_at: datetime = Field(default_factory=utc_now, sa_column=Column("CreatedAt", DateTime))
    expected_arrival_at: Optional[datetime] = Field(default=None, sa_column=Column("ExpectedArrivalAt", DateTime))
