# TASK-003: Master Data Models

## Goal

مدل‌های پایه master data را بساز.

## Entities

- ImportBatch
- BOM
- BOMParts
- Order
- OrderParts
- Routing
- RoutingOperations
- Process
- ProcessType
- Machine
- WorkCenter
- MachineProcess

## Important naming rule

نام ستون‌ها تا حد ممکن شبیه CSV و دیتابیس فعلی کارخانه باشد:

```text
BOMParent_Id
BOMChild_Id
Routine_Id
Order_Id
ParentOrder_Id
ChildOrder_Id
AssignmentStatus_Id
RoutineOperation_Id
Process_Id
Machine_Id
```

## Scope

- SQLModel entities
- schema creation/migration approach
- simple read endpoints
- no full CRUD required

## Do not implement

- CSV upload/import
- simulation
- optimizer
- UI

## Required documentation updates

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/DB_SCHEMA_CHANGE_LOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/master_data.md`

## Acceptance criteria

- Tables can be created in SQL Server.
- Basic read endpoints compile and run.
- Relationships are documented.
