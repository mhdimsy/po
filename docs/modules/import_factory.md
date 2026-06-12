# ماژول: import_factory

## هدف

اعتبارسنجی و ورود فایل‌های CSV خروجی کارخانه به جدول‌های master data.

## محدوده

- دریافت مجموعه فایل‌های CSV موردنیاز به‌صورت multipart.
- endpoint مخصوص validate-only.
- گزارش validation ساخت‌یافته شامل errorها و warningها.
- endpoint import واقعی که `ImportBatch` ایجاد می‌کند.
- اگر هر error یا warning وجود داشته باشد، import انجام نمی‌شود.

## موجودیت‌ها

- `ImportBatch`
- `ImportFile`
- موجودیت‌های master data که در `docs/modules/master_data.md` آمده‌اند.

## سرویس‌ها

- `validate_csv_files`
- `run_import`

## endpointهای API

- `POST /imports/validate`
- `POST /imports/run`

## eventها

در TASK-004 و TASK-005 ندارد.

## جدول‌های current state

ردیف‌های واردشده در جدول‌های master data ذخیره می‌شوند و به `import_batch_id` ارجاع می‌دهند.

## وابستگی‌ها

- مدل‌های `master_data`
- dependency مربوط به session در `database`

## قوانین validation

- فایل‌های الزامی باید وجود داشته باشند.
- ستون‌های الزامی باید وجود داشته باشند.
- مقدارهای اصلی `Id` داخل هر فایل باید یکتا باشند.
- فرمت‌های پایه integer، number، boolean و date بررسی می‌شوند.
- ارجاع‌های FK بین فایل‌ها بررسی می‌شوند.
- duration منفی رد می‌شود.
- warningها گزارش می‌شوند و همچنان import readiness را block می‌کنند.

## محدودیت‌های فعلی

- parsing فایل CSV فعلاً UTF-8 با BOM اختیاری را فرض می‌کند.
- برای importهای ناموفق هنوز ردیف persisted در `import_validation_issues` ساخته نمی‌شود.
- درج واقعی در SQL Server در این محیط تست نشده است.

## تست‌ها

- نبود فایل‌ها errorهای blocker تولید کرد.
- یک مجموعه CSV حداقلی و معتبر در حافظه، `import_ready=True` برگرداند.
- import روی SQLite in-memory یک `ImportBatch` ساخت و ردیف‌های master data را درج کرد.
