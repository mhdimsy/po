from pydantic import BaseModel


class ValidationIssue(BaseModel):
    file_name: str
    row_number: int | None = None
    severity: str
    code: str
    message: str
    field_name: str | None = None
    raw_value: str | None = None


class FileValidationReport(BaseModel):
    file_name: str
    row_count: int
    errors: list[ValidationIssue]
    warnings: list[ValidationIssue]


class ImportValidationReport(BaseModel):
    import_ready: bool
    total_rows: int
    files: list[FileValidationReport]
    issues: list[ValidationIssue]


class ImportRunReport(BaseModel):
    import_batch_id: int
    import_ready: bool
    total_rows: int
    imported_rows_by_file: dict[str, int]
    created_entity_counts: dict[str, int]
    issues: list[ValidationIssue]
