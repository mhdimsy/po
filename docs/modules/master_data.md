# ماژول: master_data

## هدف

نگهداری داده‌های seed واردشده از کارخانه برای BOM، سفارش‌ها، routingها، processها، machineها، work centerها و import batchها.

## محدوده

- موجودیت‌های SQLModel برای master data مربوط به TASK-003.
- endpointهای فهرست‌گیری read-only.
- ساخت schema با metadata مربوط به SQLModel برای استفاده در نمونه محلی.

## موجودیت‌ها

- `ImportBatch`
- `ImportFile`
- `ImportValidationIssue`
- `BOM`
- `BOMPart`
- `ProductionOrder`
- `OrderPart`
- `Routing`
- `RoutingOperation`
- `Process`
- `ProcessType`
- `Machine`
- `WorkCenter`
- `MachineProcess`

## سرویس‌ها

- endpointهای خواندن در `backend/app/modules/master_data/router.py`.

## endpointهای API

- `GET /master-data/import-batches`
- `GET /master-data/boms`
- `GET /master-data/bom-parts`
- `GET /master-data/orders`
- `GET /master-data/order-parts`
- `GET /master-data/routings`
- `GET /master-data/routing-operations`
- `GET /master-data/processes`
- `GET /master-data/process-types`
- `GET /master-data/machines`
- `GET /master-data/work-centers`
- `GET /master-data/machine-processes`

## eventها

در محدوده این تسک‌ها ندارد.

## جدول‌های current state

این جدول‌های master data، جدول‌های مرجع/seed واردشده هستند و در ماژول‌های بعدی استفاده می‌شوند.

## وابستگی‌ها

- ماژول `database` برای sessionهای SQLModel.

## قوانین validation

در TASK-003، validation در سطح API فراتر از type fieldهای SQLModel اضافه نشده است.

## محدودیت‌های فعلی

- CRUD کامل ندارد.
- ابزار migration هنوز اضافه نشده است.
- رابطه‌ها فعلاً با source ID fieldها مستند شده‌اند، نه با foreign keyهای SQL بین source IDهای واردشده.

## تست‌ها

- metadata مربوط به SQLModel در تست verification روی SQLite in-memory با موفقیت ساخته شد.
- ثبت routeهای پایه app موفق بود.
