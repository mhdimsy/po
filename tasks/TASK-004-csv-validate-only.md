# TASK-004: CSV Import - Validate Only

## Goal

مرحله Validate Only برای CSV import را بساز. در این تسک هیچ داده‌ای وارد دیتابیس نشود.

## CSV files

- `bom.csv`
- `bom_parts.csv`
- `orders.csv`
- `order_parts.csv`
- `routings.csv`
- `routing_operations.csv`
- `processes.csv`
- `process_types.csv`
- `machines.csv`
- `work_centers.csv`
- `machine_processes.csv`

## Validation rules

- required columns بررسی شوند
- نوع داده‌های پایه بررسی شوند
- FKهای بین فایل‌ها بررسی شوند
- duplicate key بررسی شود
- warning هم blocker است
- اگر warning یا error وجود دارد، import مجاز نیست

## Scope

- upload multiple CSVs
- validate only endpoint
- validation report with errors/warnings

## Do not implement

- ImportBatch creation
- database insert
- UI
- simulation

## Required documentation updates

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/import_factory.md`
- `docs/api/import_factory.md`

## Acceptance criteria

- Endpoint returns structured validation report.
- Records are not inserted into DB.
- Any warning blocks import readiness.
