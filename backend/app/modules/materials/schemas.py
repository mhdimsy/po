from pydantic import BaseModel, Field


class GenerateInventoryRequest(BaseModel):
    preset: str = Field(default="Normal")
    warehouse_code: str = Field(default="MAIN")
    warehouse_title: str = Field(default="Main Warehouse")
    safety_stock_percent: float = Field(default=0.2, ge=0, le=10)
    create_purchase_requests: bool = True
    seed: int | None = None


class GenerateSuppliersRequest(BaseModel):
    preset: str = Field(default="Mixed")
    suppliers_per_item: int = Field(default=3, ge=1, le=10)
    seed: int | None = None


class GenerateInventoryResponse(BaseModel):
    preset: str
    warehouse_id: int
    inventory_items_created: int
    inventory_balances_created: int
    purchase_requests_created: int
    total_on_hand_qty: float


class GenerateSuppliersResponse(BaseModel):
    preset: str
    suppliers_created: int
    mappings_created: int
    default_mappings_created: int


class InventoryItemRead(BaseModel):
    id: int
    bom_id: int
    code: str
    title: str
    unit: str
    is_synthetic: bool


class InventoryBalanceRead(BaseModel):
    id: int
    inventory_item_id: int
    warehouse_id: int
    on_hand_qty: float
    reserved_qty: float
    safety_stock_qty: float
    preset: str


class SupplierRead(BaseModel):
    id: int
    code: str
    title: str
    preset_type: str
    reliability_score: float
    default_lead_time_min: int
    is_synthetic: bool


class BOMItemSupplierRead(BaseModel):
    id: int
    inventory_item_id: int
    supplier_id: int
    is_default: bool
    is_synthetic: bool


class PurchaseRequestRead(BaseModel):
    id: int
    inventory_item_id: int
    supplier_id: int | None
    shortage_qty: float
    suggested_qty: float
    final_qty: float | None
    status: str
