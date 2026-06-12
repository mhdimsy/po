from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlmodel import Field, SQLModel

from app.core.time import utc_now


class ImportBatch(SQLModel, table=True):
    __tablename__ = "import_batches"

    id: Optional[int] = Field(default=None, primary_key=True)
    batch_code: str = Field(index=True, max_length=80)
    source_name: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=utc_now)
    status: str = Field(default="Completed", max_length=40)
    notes: Optional[str] = Field(default=None, max_length=1000)


class ImportFile(SQLModel, table=True):
    __tablename__ = "import_files"

    id: Optional[int] = Field(default=None, primary_key=True)
    import_batch_id: int = Field(foreign_key="import_batches.id", index=True)
    file_name: str = Field(max_length=255)
    file_type: str = Field(max_length=80)
    row_count: int = 0
    status: str = Field(default="Imported", max_length=40)


class ImportValidationIssue(SQLModel, table=True):
    __tablename__ = "import_validation_issues"

    id: Optional[int] = Field(default=None, primary_key=True)
    import_batch_id: Optional[int] = Field(default=None, foreign_key="import_batches.id", index=True)
    file_name: str = Field(max_length=255)
    row_number: Optional[int] = None
    severity: str = Field(max_length=20)
    code: str = Field(max_length=80)
    message: str = Field(max_length=1000)
    field_name: Optional[str] = Field(default=None, max_length=120)
    raw_value: Optional[str] = Field(default=None, max_length=1000)


class BOM(SQLModel, table=True):
    __tablename__ = "boms"

    id: Optional[int] = Field(default=None, primary_key=True)
    import_batch_id: int = Field(foreign_key="import_batches.id", index=True)
    source_bom_id: int = Field(sa_column=Column("BOM_Id", Integer, index=True))
    title: Optional[str] = Field(default=None, max_length=255)
    code: Optional[str] = Field(default=None, max_length=120)
    sap_code: Optional[str] = Field(default=None, max_length=120)
    usage_type_id: Optional[int] = Field(default=None, sa_column=Column("UsageType_Id", Integer))
    parts_group_id: Optional[int] = Field(default=None, sa_column=Column("PartsGroup_Id", Integer))
    pc: Optional[str] = Field(default=None, max_length=120)


class BOMPart(SQLModel, table=True):
    __tablename__ = "bom_parts"

    id: Optional[int] = Field(default=None, primary_key=True)
    import_batch_id: int = Field(foreign_key="import_batches.id", index=True)
    source_bom_part_id: int = Field(sa_column=Column("BOMPart_Id", Integer, index=True))
    bom_parent_id: int = Field(sa_column=Column("BOMParent_Id", Integer, index=True))
    bom_child_id: int = Field(sa_column=Column("BOMChild_Id", Integer, index=True))
    quantity: float = Field(default=0, sa_column=Column("Quantity", Float))
    unit: Optional[str] = Field(default=None, max_length=40)


class ProductionOrder(SQLModel, table=True):
    __tablename__ = "production_orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    import_batch_id: int = Field(foreign_key="import_batches.id", index=True)
    source_order_id: int = Field(sa_column=Column("Order_Id", Integer, index=True))
    code: Optional[str] = Field(default=None, max_length=120)
    routine_id: Optional[int] = Field(default=None, sa_column=Column("Routine_Id", Integer, index=True))
    bom_id: Optional[int] = Field(default=None, sa_column=Column("BOM_Id", Integer, index=True))
    product_code: Optional[str] = Field(default=None, max_length=120)
    customer_name: Optional[str] = Field(default=None, max_length=255)
    order_date: Optional[datetime] = Field(default=None, sa_column=Column("OrderDate", DateTime))
    earliest_start_date: Optional[datetime] = Field(default=None, sa_column=Column("EarliestStartDate", DateTime))
    customer_requested_date: Optional[datetime] = Field(default=None, sa_column=Column("CustomerRequestedDate", DateTime))
    committed_delivery_date: Optional[datetime] = Field(default=None, sa_column=Column("CommittedDeliveryDate", DateTime))
    internal_production_due_date: Optional[datetime] = Field(default=None, sa_column=Column("InternalProductionDueDate", DateTime))
    material_required_date: Optional[datetime] = Field(default=None, sa_column=Column("MaterialRequiredDate", DateTime))
    shipment_date: Optional[datetime] = Field(default=None, sa_column=Column("ShipmentDate", DateTime))
    good_reciept: Optional[str] = Field(default=None, sa_column=Column("GoodReciept", String(120)))


class OrderPart(SQLModel, table=True):
    __tablename__ = "order_parts"

    id: Optional[int] = Field(default=None, primary_key=True)
    import_batch_id: int = Field(foreign_key="import_batches.id", index=True)
    source_order_part_id: int = Field(sa_column=Column("OrderPart_Id", Integer, index=True))
    parent_order_id: int = Field(sa_column=Column("ParentOrder_Id", Integer, index=True))
    child_order_id: int = Field(sa_column=Column("ChildOrder_Id", Integer, index=True))
    assignment_status_id: Optional[int] = Field(default=None, sa_column=Column("AssignmentStatus_Id", Integer))
    assignment_status_title: Optional[str] = Field(default=None, sa_column=Column("AssignmentStatusTitle", String(120)))


class Routing(SQLModel, table=True):
    __tablename__ = "routings"

    id: Optional[int] = Field(default=None, primary_key=True)
    import_batch_id: int = Field(foreign_key="import_batches.id", index=True)
    source_routine_id: int = Field(sa_column=Column("Routine_Id", Integer, index=True))
    bom_id: Optional[int] = Field(default=None, sa_column=Column("BOM_Id", Integer, index=True))
    title: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True, sa_column=Column("IsActive", Boolean))


class RoutingOperation(SQLModel, table=True):
    __tablename__ = "routing_operations"

    id: Optional[int] = Field(default=None, primary_key=True)
    import_batch_id: int = Field(foreign_key="import_batches.id", index=True)
    source_routine_operation_id: int = Field(sa_column=Column("RoutineOperation_Id", Integer, index=True))
    routine_id: int = Field(sa_column=Column("Routine_Id", Integer, index=True))
    process_id: int = Field(sa_column=Column("Process_Id", Integer, index=True))
    operation_sequence: Optional[int] = Field(default=None, sa_column=Column("OperationSequence", Integer))
    operation_description: Optional[str] = Field(default=None, sa_column=Column("OperationDescription", String(1000)))
    setup_duration: Optional[int] = Field(default=None, sa_column=Column("SetupDuration", Integer))
    operation_duration: Optional[int] = Field(default=None, sa_column=Column("OperationDuration", Integer))
    assembly_duration: Optional[int] = Field(default=None, sa_column=Column("AssemblyDuration", Integer))
    requires_qc: bool = Field(default=False, sa_column=Column("RequiresQC", Boolean))
    is_interruptible: bool = Field(default=False, sa_column=Column("IsInterruptible", Boolean))
    can_outsource: bool = Field(default=False, sa_column=Column("CanOutsource", Boolean))
    outsource_lead_time_minutes: Optional[int] = Field(default=None, sa_column=Column("OutsourceLeadTimeMinutes", Integer))


class ProcessType(SQLModel, table=True):
    __tablename__ = "process_types"

    id: Optional[int] = Field(default=None, primary_key=True)
    import_batch_id: int = Field(foreign_key="import_batches.id", index=True)
    source_process_type_id: int = Field(sa_column=Column("ProcessType_Id", Integer, index=True))
    title: Optional[str] = Field(default=None, max_length=255)


class Process(SQLModel, table=True):
    __tablename__ = "processes"

    id: Optional[int] = Field(default=None, primary_key=True)
    import_batch_id: int = Field(foreign_key="import_batches.id", index=True)
    source_process_id: int = Field(sa_column=Column("Process_Id", Integer, index=True))
    title: Optional[str] = Field(default=None, max_length=255)
    process_type_id: Optional[int] = Field(default=None, sa_column=Column("ProcessType_Id", Integer, index=True))


class WorkCenter(SQLModel, table=True):
    __tablename__ = "work_centers"

    id: Optional[int] = Field(default=None, primary_key=True)
    import_batch_id: int = Field(foreign_key="import_batches.id", index=True)
    source_work_center_id: int = Field(sa_column=Column("WorkCenter_Id", Integer, index=True))
    code: Optional[str] = Field(default=None, max_length=120)
    title: Optional[str] = Field(default=None, max_length=255)


class Machine(SQLModel, table=True):
    __tablename__ = "machines"

    id: Optional[int] = Field(default=None, primary_key=True)
    import_batch_id: int = Field(foreign_key="import_batches.id", index=True)
    source_machine_id: int = Field(sa_column=Column("Machine_Id", Integer, index=True))
    title: Optional[str] = Field(default=None, max_length=255)
    barcode: Optional[str] = Field(default=None, max_length=120)
    work_center_id: int = Field(sa_column=Column("WorkCenter_Id", Integer, index=True))
    status: Optional[str] = Field(default=None, max_length=80)


class MachineProcess(SQLModel, table=True):
    __tablename__ = "machine_processes"

    id: Optional[int] = Field(default=None, primary_key=True)
    import_batch_id: int = Field(foreign_key="import_batches.id", index=True)
    source_machine_process_id: int = Field(sa_column=Column("MachineProcess_Id", Integer, index=True))
    machine_id: int = Field(sa_column=Column("Machine_Id", Integer, index=True))
    process_id: int = Field(sa_column=Column("Process_Id", Integer, index=True))
    is_primary: bool = Field(default=False, sa_column=Column("IsPrimary", Boolean))
    setup_factor: float = Field(default=1, sa_column=Column("SetupFactor", Float))
    processing_factor: float = Field(default=1, sa_column=Column("ProcessingFactor", Float))
