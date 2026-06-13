from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Callable

from sqlmodel import Session

from app.core.db import get_engine, reset_db_and_tables
from app.core.time import utc_now
from app.modules.import_factory.schemas import (
    FileValidationReport,
    ImportRunReport,
    ImportValidationReport,
    RebuildDemoRequest,
    RebuildDemoResponse,
    ValidationIssue,
)
from app.modules.master_data.models import (
    BOM,
    BOMPart,
    ImportBatch,
    ImportFile,
    Machine,
    MachineProcess,
    OrderPart,
    Process,
    ProcessType,
    ProductionOrder,
    Routing,
    RoutingOperation,
    WorkCenter,
)
from app.modules.scenarios.models import Scenario
from app.modules.scenarios.schemas import ScenarioSeedRequest
from app.modules.scenarios.service import seed_scenario_from_master_data
from scripts.repair_import_data import main as repair_import_data


CSV_FILE_ORDER = [
    "process_types.csv",
    "processes.csv",
    "work_centers.csv",
    "machines.csv",
    "machine_processes.csv",
    "bom.csv",
    "bom_parts.csv",
    "routings.csv",
    "routing_operations.csv",
    "orders.csv",
    "order_parts.csv",
]

IMPORT_DATA_DIR = Path(__file__).resolve().parents[3] / "import_data"


@dataclass(frozen=True)
class CsvSpec:
    required_columns: tuple[str, ...]
    int_columns: tuple[str, ...] = ()
    float_columns: tuple[str, ...] = ()
    bool_columns: tuple[str, ...] = ()
    date_columns: tuple[str, ...] = ()
    non_negative_columns: tuple[str, ...] = ()


CSV_SPECS: dict[str, CsvSpec] = {
    "bom.csv": CsvSpec(("Id", "Title", "Code", "SAPCode", "UsageType_Id", "PartsGroup_Id", "PC"), ("Id", "UsageType_Id", "PartsGroup_Id")),
    "bom_parts.csv": CsvSpec(("Id", "BOMParent_Id", "BOMChild_Id", "Quantity", "Unit"), ("Id", "BOMParent_Id", "BOMChild_Id"), ("Quantity",)),
    "orders.csv": CsvSpec(
        (
            "Id",
            "Code",
            "Routine_Id",
            "BOM_Id",
            "ProductCode",
            "CustomerName",
            "OrderDate",
            "EarliestStartDate",
            "CustomerRequestedDate",
            "CommittedDeliveryDate",
            "InternalProductionDueDate",
            "MaterialRequiredDate",
            "ShipmentDate",
            "GoodReciept",
        ),
        ("Id", "Routine_Id", "BOM_Id"),
        date_columns=(
            "OrderDate",
            "EarliestStartDate",
            "CustomerRequestedDate",
            "CommittedDeliveryDate",
            "InternalProductionDueDate",
            "MaterialRequiredDate",
            "ShipmentDate",
        ),
    ),
    "order_parts.csv": CsvSpec(("Id", "ParentOrder_Id", "ChildOrder_Id", "AssignmentStatus_Id", "AssignmentStatusTitle"), ("Id", "ParentOrder_Id", "ChildOrder_Id", "AssignmentStatus_Id")),
    "routings.csv": CsvSpec(("Id", "BOM_Id", "Title", "IsActive"), ("Id", "BOM_Id"), bool_columns=("IsActive",)),
    "routing_operations.csv": CsvSpec(
        (
            "Id",
            "Routine_Id",
            "Process_Id",
            "OperationSequence",
            "OperationDescription",
            "SetupDuration",
            "OperationDuration",
            "AssemblyDuration",
            "RequiresQC",
            "IsInterruptible",
            "CanOutsource",
            "OutsourceLeadTimeMinutes",
        ),
        ("Id", "Routine_Id", "Process_Id", "OperationSequence", "SetupDuration", "OperationDuration", "AssemblyDuration", "OutsourceLeadTimeMinutes"),
        bool_columns=("RequiresQC", "IsInterruptible", "CanOutsource"),
        non_negative_columns=("SetupDuration", "OperationDuration", "AssemblyDuration", "OutsourceLeadTimeMinutes"),
    ),
    "processes.csv": CsvSpec(("Id", "Title", "ProcessType_Id"), ("Id", "ProcessType_Id")),
    "process_types.csv": CsvSpec(("Id", "Title"), ("Id",)),
    "work_centers.csv": CsvSpec(("Id", "Code", "Title"), ("Id",)),
    "machines.csv": CsvSpec(("Id", "Title", "Barcode", "WorkCenter_Id", "Status"), ("Id", "WorkCenter_Id")),
    "machine_processes.csv": CsvSpec(("Id", "Machine_Id", "Process_Id", "IsPrimary", "SetupFactor", "ProcessingFactor"), ("Id", "Machine_Id", "Process_Id"), ("SetupFactor", "ProcessingFactor"), ("IsPrimary",)),
}


def decode_csv(content: bytes) -> list[dict[str, str]]:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(StringIO(text))
    return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def validate_csv_files(files: dict[str, bytes]) -> ImportValidationReport:
    rows_by_file: dict[str, list[dict[str, str]]] = {}
    issues: list[ValidationIssue] = []
    file_reports: list[FileValidationReport] = []

    for file_name, spec in CSV_SPECS.items():
        if file_name not in files:
            issues.append(issue(file_name, None, "Error", "MISSING_FILE", f"Required file {file_name} is missing."))
            rows_by_file[file_name] = []
            continue
        try:
            rows = decode_csv(files[file_name])
        except UnicodeDecodeError as exc:
            issues.append(issue(file_name, None, "Error", "INVALID_ENCODING", str(exc)))
            rows = []
        rows_by_file[file_name] = rows
        validate_columns(file_name, rows, spec, issues)
        validate_rows(file_name, rows, spec, issues)

    validate_cross_file_rules(rows_by_file, issues)

    total_rows = sum(len(rows) for rows in rows_by_file.values())
    for file_name in CSV_SPECS:
        file_issues = [item for item in issues if item.file_name == file_name]
        file_reports.append(
            FileValidationReport(
                file_name=file_name,
                row_count=len(rows_by_file.get(file_name, [])),
                errors=[item for item in file_issues if item.severity == "Error"],
                warnings=[item for item in file_issues if item.severity == "Warning"],
            )
        )

    return ImportValidationReport(
        import_ready=not issues,
        total_rows=total_rows,
        files=file_reports,
        issues=issues,
    )


def validate_columns(file_name: str, rows: list[dict[str, str]], spec: CsvSpec, issues: list[ValidationIssue]) -> None:
    if not rows:
        return
    actual_columns = set(rows[0].keys())
    for column in spec.required_columns:
        if column not in actual_columns:
            issues.append(issue(file_name, None, "Error", "MISSING_COLUMN", f"Required column {column} is missing.", column))


def validate_rows(file_name: str, rows: list[dict[str, str]], spec: CsvSpec, issues: list[ValidationIssue]) -> None:
    seen_ids: set[str] = set()
    for index, row in enumerate(rows, start=2):
        row_id = row.get("Id", "")
        if not row_id:
            issues.append(issue(file_name, index, "Error", "MISSING_ID", "Id is required.", "Id"))
        elif row_id in seen_ids:
            issues.append(issue(file_name, index, "Error", "DUPLICATE_ID", f"Duplicate Id {row_id}.", "Id", row_id))
        seen_ids.add(row_id)

        for column in spec.int_columns:
            validate_optional_int(file_name, index, row, column, issues)
        for column in spec.float_columns:
            validate_optional_float(file_name, index, row, column, issues)
        for column in spec.bool_columns:
            validate_optional_bool(file_name, index, row, column, issues)
        for column in spec.date_columns:
            validate_optional_datetime(file_name, index, row, column, issues)
        for column in spec.non_negative_columns:
            value = row.get(column, "")
            if value and parse_float(value) is not None and parse_float(value) < 0:
                issues.append(issue(file_name, index, "Error", "NEGATIVE_VALUE", f"{column} cannot be negative.", column, value))


def validate_cross_file_rules(rows_by_file: dict[str, list[dict[str, str]]], issues: list[ValidationIssue]) -> None:
    ids = {file_name: {row.get("Id", "") for row in rows if row.get("Id", "")} for file_name, rows in rows_by_file.items()}

    require_fk(rows_by_file, issues, "bom_parts.csv", "BOMParent_Id", ids["bom.csv"])
    require_fk(rows_by_file, issues, "bom_parts.csv", "BOMChild_Id", ids["bom.csv"])
    require_fk(rows_by_file, issues, "orders.csv", "Routine_Id", ids["routings.csv"])
    require_fk(rows_by_file, issues, "orders.csv", "BOM_Id", ids["bom.csv"])
    require_fk(rows_by_file, issues, "order_parts.csv", "ParentOrder_Id", ids["orders.csv"])
    require_fk(rows_by_file, issues, "order_parts.csv", "ChildOrder_Id", ids["orders.csv"])
    require_fk(rows_by_file, issues, "routings.csv", "BOM_Id", ids["bom.csv"])
    require_fk(rows_by_file, issues, "routing_operations.csv", "Routine_Id", ids["routings.csv"])
    require_fk(rows_by_file, issues, "routing_operations.csv", "Process_Id", ids["processes.csv"])
    require_fk(rows_by_file, issues, "processes.csv", "ProcessType_Id", ids["process_types.csv"], allow_blank=True)
    require_fk(rows_by_file, issues, "machines.csv", "WorkCenter_Id", ids["work_centers.csv"])
    require_fk(rows_by_file, issues, "machine_processes.csv", "Machine_Id", ids["machines.csv"])
    require_fk(rows_by_file, issues, "machine_processes.csv", "Process_Id", ids["processes.csv"])

    machine_ids_with_capability = {row.get("Machine_Id", "") for row in rows_by_file["machine_processes.csv"]}
    for index, row in enumerate(rows_by_file["machines.csv"], start=2):
        if row.get("Id", "") not in machine_ids_with_capability:
            issues.append(issue("machines.csv", index, "Warning", "MACHINE_WITHOUT_CAPABILITY", "Machine has no process capability.", "Id", row.get("Id", "")))

    bom_parent_ids = {row.get("BOMParent_Id", "") for row in rows_by_file["bom_parts.csv"]}
    for index, row in enumerate(rows_by_file["bom.csv"], start=2):
        if row.get("Id", "") and not row.get("Title", ""):
            issues.append(issue("bom.csv", index, "Warning", "BOM_WITHOUT_TITLE", "BOM item has no title.", "Title"))
        if row.get("Id", "") not in bom_parent_ids and is_assembly_like_bom(row):
            issues.append(issue("bom.csv", index, "Warning", "BOM_WITHOUT_CHILD", "BOM parent has no child and may be expected as assembly.", "Id", row.get("Id", "")))

    routine_ids_with_operation = {row.get("Routine_Id", "") for row in rows_by_file["routing_operations.csv"]}
    for index, row in enumerate(rows_by_file["routings.csv"], start=2):
        if row.get("Id", "") not in routine_ids_with_operation:
            issues.append(issue("routings.csv", index, "Warning", "ROUTING_WITHOUT_OPERATION", "Routing has no operation.", "Id", row.get("Id", "")))

    for index, row in enumerate(rows_by_file["routing_operations.csv"], start=2):
        if not row.get("Routine_Id", "") or not row.get("Process_Id", ""):
            issues.append(issue("routing_operations.csv", index, "Error", "OPERATION_MISSING_REQUIRED_FK", "Operation requires Routine_Id and Process_Id."))
        durations = [row.get("SetupDuration", ""), row.get("OperationDuration", ""), row.get("AssemblyDuration", "")]
        if not any(value and parse_float(value) and parse_float(value) > 0 for value in durations):
            issues.append(issue("routing_operations.csv", index, "Warning", "OPERATION_WITHOUT_STANDARD_DURATION", "RoutingOperation has no standard duration."))

    for index, row in enumerate(rows_by_file["processes.csv"], start=2):
        if not row.get("ProcessType_Id", ""):
            issues.append(issue("processes.csv", index, "Warning", "PROCESS_WITHOUT_TYPE", "Process has no ProcessType_Id.", "ProcessType_Id"))

    for index, row in enumerate(rows_by_file["order_parts.csv"], start=2):
        if not row.get("AssignmentStatus_Id", "") and not row.get("AssignmentStatusTitle", ""):
            issues.append(issue("order_parts.csv", index, "Warning", "ORDER_ASSIGNMENT_STATUS_EMPTY", "Order child assignment status is empty."))


def require_fk(
    rows_by_file: dict[str, list[dict[str, str]]],
    issues: list[ValidationIssue],
    file_name: str,
    field_name: str,
    allowed_ids: set[str],
    allow_blank: bool = False,
) -> None:
    for index, row in enumerate(rows_by_file[file_name], start=2):
        value = row.get(field_name, "")
        if not value and allow_blank:
            continue
        if not value:
            issues.append(issue(file_name, index, "Error", "MISSING_FK", f"{field_name} is required.", field_name))
        elif value not in allowed_ids:
            issues.append(issue(file_name, index, "Error", "MISSING_FK_TARGET", f"{field_name} target {value} was not found.", field_name, value))


def run_import(session: Session, files: dict[str, bytes], source_name: str | None = None) -> ImportRunReport:
    validation = validate_csv_files(files)
    if not validation.import_ready:
        return ImportRunReport(
            import_batch_id=0,
            import_ready=False,
            total_rows=validation.total_rows,
            imported_rows_by_file={},
            created_entity_counts={},
            issues=validation.issues,
        )

    batch = ImportBatch(
        batch_code=f"IMPORT-{utc_now().strftime('%Y%m%d%H%M%S')}",
        source_name=source_name,
        status="Completed",
    )
    session.add(batch)
    session.flush()

    rows_by_file = {file_name: decode_csv(files[file_name]) for file_name in CSV_FILE_ORDER}
    imported_rows_by_file: dict[str, int] = {}
    created_entity_counts: dict[str, int] = {}

    for file_name in CSV_FILE_ORDER:
        rows = rows_by_file[file_name]
        session.add(ImportFile(import_batch_id=batch.id, file_name=file_name, file_type=file_name.removesuffix(".csv"), row_count=len(rows)))
        importer = IMPORTERS[file_name]
        for row in rows:
            session.add(importer(row, batch.id))
        imported_rows_by_file[file_name] = len(rows)
        created_entity_counts[file_name.removesuffix(".csv")] = len(rows)

    session.commit()

    return ImportRunReport(
        import_batch_id=batch.id or 0,
        import_ready=True,
        total_rows=validation.total_rows,
        imported_rows_by_file=imported_rows_by_file,
        created_entity_counts=created_entity_counts,
        issues=[],
    )


def reset_database_and_import_from_folder(source_name: str | None = None) -> ImportRunReport:
    files = read_import_folder()
    validation = validate_csv_files(files)
    if not validation.import_ready:
        return ImportRunReport(
            import_batch_id=0,
            import_ready=False,
            total_rows=validation.total_rows,
            imported_rows_by_file={},
            created_entity_counts={},
            issues=validation.issues,
        )

    reset_db_and_tables()
    engine = get_engine()
    if engine is None:
        raise RuntimeError("Database connection string is not configured.")
    with Session(engine) as session:
        return run_import(session, files, source_name=source_name or "folder-reset-import")


def rebuild_demo_database(request: RebuildDemoRequest) -> RebuildDemoResponse:
    repair_import_data()
    import_report = reset_database_and_import_from_folder(source_name="one-click-demo-rebuild")
    if not import_report.import_ready:
        return RebuildDemoResponse(
            import_report=import_report,
            scenario_id=0,
            scenario_name=request.scenario_name,
            orders_seeded=0,
            operations_seeded=0,
            machines_seeded=0,
        )

    engine = get_engine()
    if engine is None:
        raise RuntimeError("Database connection string is not configured.")
    with Session(engine) as session:
        scenario = Scenario(
            name=request.scenario_name,
            base_import_batch_id=import_report.import_batch_id,
            status="Draft",
            notes="Created by one-click demo rebuild.",
        )
        session.add(scenario)
        session.commit()
        session.refresh(scenario)
        seed = seed_scenario_from_master_data(
            session,
            scenario.id,
            ScenarioSeedRequest(
                import_batch_id=import_report.import_batch_id,
                max_orders=request.max_orders,
                reset_existing_state=True,
            ),
        )
        return RebuildDemoResponse(
            import_report=import_report,
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            orders_seeded=seed.orders_seeded,
            operations_seeded=seed.operations_seeded,
            machines_seeded=seed.machines_seeded,
        )


def read_import_folder() -> dict[str, bytes]:
    if not IMPORT_DATA_DIR.exists():
        raise RuntimeError(f"Import folder was not found: {IMPORT_DATA_DIR}")
    files: dict[str, bytes] = {}
    for file_name in CSV_FILE_ORDER:
        file_path = IMPORT_DATA_DIR / file_name
        if file_path.exists():
            files[file_name] = file_path.read_bytes()
    return files


def issue(file_name: str, row_number: int | None, severity: str, code: str, message: str, field_name: str | None = None, raw_value: str | None = None) -> ValidationIssue:
    return ValidationIssue(file_name=file_name, row_number=row_number, severity=severity, code=code, message=message, field_name=field_name, raw_value=raw_value)


def is_assembly_like_bom(row: dict[str, str]) -> bool:
    values = " ".join([row.get("PC", ""), row.get("Title", ""), row.get("Code", "")]).lower()
    return any(marker in values for marker in ("assembly", "assy", "مونتاژ"))


def parse_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def parse_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def validate_optional_int(file_name: str, row_number: int, row: dict[str, str], column: str, issues: list[ValidationIssue]) -> None:
    value = row.get(column, "")
    if value and parse_int(value) is None:
        issues.append(issue(file_name, row_number, "Error", "INVALID_INTEGER", f"{column} must be an integer.", column, value))


def validate_optional_float(file_name: str, row_number: int, row: dict[str, str], column: str, issues: list[ValidationIssue]) -> None:
    value = row.get(column, "")
    if value and parse_float(value) is None:
        issues.append(issue(file_name, row_number, "Error", "INVALID_NUMBER", f"{column} must be a number.", column, value))


def validate_optional_bool(file_name: str, row_number: int, row: dict[str, str], column: str, issues: list[ValidationIssue]) -> None:
    value = row.get(column, "")
    if value and value.lower() not in {"1", "0", "true", "false", "yes", "no", "y", "n"}:
        issues.append(issue(file_name, row_number, "Error", "INVALID_BOOLEAN", f"{column} must be a boolean.", column, value))


def validate_optional_datetime(file_name: str, row_number: int, row: dict[str, str], column: str, issues: list[ValidationIssue]) -> None:
    value = row.get(column, "")
    if value and parse_datetime(value) is None:
        issues.append(issue(file_name, row_number, "Error", "INVALID_DATE", f"{column} has invalid date format.", column, value))


def required_int(row: dict[str, str], column: str) -> int:
    value = parse_int(row.get(column, ""))
    if value is None:
        raise ValueError(f"{column} is required.")
    return value


def optional_int(row: dict[str, str], column: str) -> int | None:
    return parse_int(row.get(column, ""))


def optional_float(row: dict[str, str], column: str, default: float | None = None) -> float | None:
    return parse_float(row.get(column, "")) if row.get(column, "") != "" else default


def import_bom(row: dict[str, str], batch_id: int) -> BOM:
    return BOM(import_batch_id=batch_id, source_bom_id=required_int(row, "Id"), title=row.get("Title"), code=row.get("Code"), sap_code=row.get("SAPCode"), usage_type_id=optional_int(row, "UsageType_Id"), parts_group_id=optional_int(row, "PartsGroup_Id"), pc=row.get("PC"))


def import_bom_part(row: dict[str, str], batch_id: int) -> BOMPart:
    return BOMPart(import_batch_id=batch_id, source_bom_part_id=required_int(row, "Id"), bom_parent_id=required_int(row, "BOMParent_Id"), bom_child_id=required_int(row, "BOMChild_Id"), quantity=optional_float(row, "Quantity", 0) or 0, unit=row.get("Unit"))


def import_order(row: dict[str, str], batch_id: int) -> ProductionOrder:
    return ProductionOrder(import_batch_id=batch_id, source_order_id=required_int(row, "Id"), code=row.get("Code"), routine_id=optional_int(row, "Routine_Id"), bom_id=optional_int(row, "BOM_Id"), product_code=row.get("ProductCode"), customer_name=row.get("CustomerName"), order_date=parse_datetime(row.get("OrderDate")), earliest_start_date=parse_datetime(row.get("EarliestStartDate")), customer_requested_date=parse_datetime(row.get("CustomerRequestedDate")), committed_delivery_date=parse_datetime(row.get("CommittedDeliveryDate")), internal_production_due_date=parse_datetime(row.get("InternalProductionDueDate")), material_required_date=parse_datetime(row.get("MaterialRequiredDate")), shipment_date=parse_datetime(row.get("ShipmentDate")), good_reciept=row.get("GoodReciept"))


def import_order_part(row: dict[str, str], batch_id: int) -> OrderPart:
    return OrderPart(import_batch_id=batch_id, source_order_part_id=required_int(row, "Id"), parent_order_id=required_int(row, "ParentOrder_Id"), child_order_id=required_int(row, "ChildOrder_Id"), assignment_status_id=optional_int(row, "AssignmentStatus_Id"), assignment_status_title=row.get("AssignmentStatusTitle"))


def import_routing(row: dict[str, str], batch_id: int) -> Routing:
    return Routing(import_batch_id=batch_id, source_routine_id=required_int(row, "Id"), bom_id=optional_int(row, "BOM_Id"), title=row.get("Title"), is_active=parse_bool(row.get("IsActive")))


def import_routing_operation(row: dict[str, str], batch_id: int) -> RoutingOperation:
    return RoutingOperation(import_batch_id=batch_id, source_routine_operation_id=required_int(row, "Id"), routine_id=required_int(row, "Routine_Id"), process_id=required_int(row, "Process_Id"), operation_sequence=optional_int(row, "OperationSequence"), operation_description=row.get("OperationDescription"), setup_duration=optional_int(row, "SetupDuration"), operation_duration=optional_int(row, "OperationDuration"), assembly_duration=optional_int(row, "AssemblyDuration"), requires_qc=parse_bool(row.get("RequiresQC")), is_interruptible=parse_bool(row.get("IsInterruptible")), can_outsource=parse_bool(row.get("CanOutsource")), outsource_lead_time_minutes=optional_int(row, "OutsourceLeadTimeMinutes"))


def import_process(row: dict[str, str], batch_id: int) -> Process:
    return Process(import_batch_id=batch_id, source_process_id=required_int(row, "Id"), title=row.get("Title"), process_type_id=optional_int(row, "ProcessType_Id"))


def import_process_type(row: dict[str, str], batch_id: int) -> ProcessType:
    return ProcessType(import_batch_id=batch_id, source_process_type_id=required_int(row, "Id"), title=row.get("Title"))


def import_work_center(row: dict[str, str], batch_id: int) -> WorkCenter:
    return WorkCenter(import_batch_id=batch_id, source_work_center_id=required_int(row, "Id"), code=row.get("Code"), title=row.get("Title"))


def import_machine(row: dict[str, str], batch_id: int) -> Machine:
    return Machine(import_batch_id=batch_id, source_machine_id=required_int(row, "Id"), title=row.get("Title"), barcode=row.get("Barcode"), work_center_id=required_int(row, "WorkCenter_Id"), status=row.get("Status"))


def import_machine_process(row: dict[str, str], batch_id: int) -> MachineProcess:
    return MachineProcess(import_batch_id=batch_id, source_machine_process_id=required_int(row, "Id"), machine_id=required_int(row, "Machine_Id"), process_id=required_int(row, "Process_Id"), is_primary=parse_bool(row.get("IsPrimary")), setup_factor=optional_float(row, "SetupFactor", 1) or 1, processing_factor=optional_float(row, "ProcessingFactor", 1) or 1)


IMPORTERS: dict[str, Callable[[dict[str, str], int], object]] = {
    "bom.csv": import_bom,
    "bom_parts.csv": import_bom_part,
    "orders.csv": import_order,
    "order_parts.csv": import_order_part,
    "routings.csv": import_routing,
    "routing_operations.csv": import_routing_operation,
    "processes.csv": import_process,
    "process_types.csv": import_process_type,
    "work_centers.csv": import_work_center,
    "machines.csv": import_machine,
    "machine_processes.csv": import_machine_process,
}
