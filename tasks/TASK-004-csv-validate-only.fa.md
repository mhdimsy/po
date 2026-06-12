# TASK-004: اعتبارسنجی CSV بدون Import

## هدف

مرحله Validate Only برای CSV import را بساز. در این تسک هیچ داده‌ای وارد دیتابیس نشود.

## فایل‌های CSV

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

## قوانین validation

- ستون‌های الزامی بررسی شوند.
- نوع داده‌های پایه بررسی شوند.
- FKهای بین فایل‌ها بررسی شوند.
- کلید تکراری بررسی شود.
- warning هم blocker است.
- اگر warning یا error وجود دارد، import مجاز نیست.

## محدوده

- upload چند فایل CSV
- endpoint مخصوص validate-only
- گزارش validation همراه با errors/warnings

## پیاده‌سازی نکن

- ساخت ImportBatch
- insert در دیتابیس
- UI
- simulation

## مستندات الزامی بعد از اجرا

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/import_factory.md`
- `docs/api/import_factory.md`

## معیار پذیرش

- endpoint گزارش validation ساخت‌یافته برگرداند.
- هیچ رکوردی در دیتابیس insert نشود.
- هر warning باعث شود import آماده اجرا نباشد.
