# TASK-014: QC / NCR / Approval

## هدف

QC/NCR/Approval را اضافه کن.

## محدوده

- QC به‌عنوان operation واقعی
- نتیجه QC دستی: Pass/Fail
- مدیریت Fail:
  - simple rework
  - rework routing
  - scrap
  - replacement order
- مدل NCR و status workflow
- approval workflow ساده:
  - QC
  - Engineering
  - Production Manager
- تصمیم approval دستی است.
- approval تأخیردار، operationهای وابسته را block می‌کند.

## پیاده‌سازی نکن

- AI برای NCR
- cost model
- approval rule engine پیچیده

## مستندات الزامی بعد از اجرا

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/DB_SCHEMA_CHANGE_LOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/qc_ncr_approval.md`

## معیار پذیرش

- QC Pass اجازه ادامه بدهد.
- QC Fail بتواند مسیر NCR/rework/scrap/replacement ایجاد کند.
- approval waiting بتواند operationهای وابسته را block کند.
