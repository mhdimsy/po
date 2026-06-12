# TASK-005: ورود CSV همراه با ImportBatch

## هدف

بعد از Validate Only، import واقعی را پیاده کن.

## محدوده

- ساخت ImportBatch
- insert ردیف‌های CSV اعتبارسنجی‌شده در جدول‌های master
- import نسخه‌دار
- گزارش تعداد ردیف‌های import شده
- block کردن import اگر هر error یا warning وجود داشته باشد

## پیاده‌سازی نکن

- UI
- scenario migration
- simulation
- optimizer

## مستندات الزامی بعد از اجرا

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/DB_SCHEMA_CHANGE_LOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/import_factory.md`
- `docs/api/import_factory.md`

## معیار پذیرش

- import یک ImportBatch جدید بسازد.
- رکوردهای import شده به ImportBatch ارجاع بدهند.
- اگر validation شامل warning یا error باشد، import شکست بخورد.
