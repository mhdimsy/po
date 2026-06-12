# TASK-003: مدل‌های Master Data

## هدف

مدل‌های پایه master data را بساز.

## موجودیت‌ها

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

## قانون مهم نام‌گذاری

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

## محدوده

- موجودیت‌های SQLModel
- رویکرد ساخت schema یا migration
- endpointهای ساده read
- CRUD کامل لازم نیست

## پیاده‌سازی نکن

- upload/import فایل CSV
- simulation
- optimizer
- UI

## مستندات الزامی بعد از اجرا

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/DB_SCHEMA_CHANGE_LOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/master_data.md`

## معیار پذیرش

- جدول‌ها بتوانند در SQL Server ساخته شوند.
- endpointهای read پایه compile و اجرا شوند.
- رابطه‌ها مستند شده باشند.
