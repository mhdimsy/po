# ماژول: qc_ncr_approval

## هدف

پیاده‌سازی workflow پایه QC، NCR و approval دستی برای کنترل کیفیت و مسدودسازی عملیات وابسته در V1.

## محدوده

- QC به‌عنوان operation واقعی از مسیر event/current state.
- نتیجه QC به‌صورت دستی: `Pass` یا `Fail`.
- مسیرهای fail:
  - `SimpleRework`
  - `ReworkRoute`
  - `Scrap`
  - `Replacement`
  - `NCR`
- مدل NCR و status workflow پایه.
- approval دستی با سه step:
  - `QC`
  - `Engineering`
  - `Production Manager`
- approval در انتظار، operation مرتبط را block می‌کند.

## موجودیت‌ها

- `QcCheck`
- `Ncr`
- `NcrApproval`
- `ReworkOrder`
- `ReplacementOrder`

## سرویس‌ها

- `start_qc`
- `submit_qc_result`
- `decide_approval`
- `list_qc_checks`
- `list_ncrs`
- `list_approvals`

## endpointهای API

- `POST /qc-ncr/checks`
- `POST /qc-ncr/checks/{qc_check_id}/result`
- `GET /qc-ncr/checks`
- `GET /qc-ncr/ncrs`
- `GET /qc-ncr/approvals`
- `POST /qc-ncr/approvals/{approval_id}/decision`

## eventها

این ماژول eventهای زیر را ثبت می‌کند:

- `QCStarted`
- `QCPassed`
- `QCFailed`
- `NCROpened`
- `NCRApprovalRequested`
- `NCRApproved`
- `NCRRejected`
- `NCRDispositionDecided`
- `ReworkCreated`
- `ReplacementOrderCreated`

## جدول‌های current state

این ماژول جدول current state جدید اضافه نمی‌کند. تغییرات وضعیت operation از مسیر event projection روی `current_operation_states` اعمال می‌شود.

نمونه وضعیت‌ها:

- QC pass: `Finished`
- QC fail: `BlockedByNCR`
- approval waiting: `WaitingQCApproval`
- rework path: `Rework`
- scrap path: `Scrap`
- replacement path: `WaitingReplacement`

## وابستگی‌ها

- `events_and_state`
- `current_operation_states`
- `scenarios`

## قوانین validation

- نتیجه QC فقط `Pass` یا `Fail` است.
- disposition فعلی فقط یکی از `NCR`، `SimpleRework`، `ReworkRoute`، `Scrap` یا `Replacement` است.
- approval decision فقط `Approved` یا `Rejected` است.
- approvalها دستی هستند.

## محدودیت‌های فعلی

- AI برای NCR وجود ندارد.
- cost model وجود ندارد.
- approval rule engine پیچیده پیاده‌سازی نشده است.
- dependent operationهای چندسطحی هنوز graph واقعی ندارند و operation مرتبط مستقیم block می‌شود.
- اجرای واقعی روی SQL Server در این محیط تست نشده است.

## تست‌ها

- `python3 -m compileall backend/app` موفق بود.
- routeهای `/qc-ncr/*` ثبت شدند.
- تست SQLite in-memory برای QC pass موفق بود و operation به `Finished` رفت.
- تست SQLite in-memory برای QC fail با disposition `SimpleRework` موفق بود.
- یک NCR، سه approval step و یک rework order ساخته شد.
- بعد از approve شدن هر سه approval، operation به `Rework` رفت.
