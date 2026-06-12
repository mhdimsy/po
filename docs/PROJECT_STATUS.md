# وضعیت پروژه

## وضعیت فعلی

زیرساخت پروژه، لایه اتصال SQL Server، مدل‌های master data، validate-only برای CSV، import CSV همراه با `ImportBatch`، generator منابع انسانی synthetic، generator موجودی/supplier synthetic، event store/current state پایه، Scenario/Snapshot پایه، simulation engine حداقلی، optimizer اولیه بدون AI، UI اولیه، Gantt/drag-drop اولیه، QC/NCR/Approval پایه، داشبورد مدیریتی و Risk Rule Engine بدون AI پیاده‌سازی شده‌اند.

## تسک جاری

TASK-015 تکمیل شده است.

## تسک‌های انجام‌شده

- `TASK-001-project-skeleton.md`
- `TASK-002-sqlserver-connection.md`
- `TASK-003-master-data-models.md`
- `TASK-004-csv-validate-only.md`
- `TASK-005-csv-import-with-import-batch.md`
- `TASK-006-synthetic-human-resources.md`
- `TASK-007-synthetic-inventory-and-suppliers.md`
- `TASK-008-event-store-current-state.md`
- `TASK-009-scenario-and-snapshot.md`
- `TASK-010-minimal-simulation-engine.md`
- `TASK-011-initial-optimizer-no-ai.md`
- `TASK-012-initial-ui.md`
- `TASK-013-gantt-and-drag-drop.md`
- `TASK-014-qc-ncr-approval.md`
- `TASK-015-dashboard-and-risk-engine.md`

## تسک بعدی پیشنهادی

در حال حاضر تسک بعدی مشخص نشده است.

## تصمیم‌های مهم فعال

- V1 بدون AI/ML واقعی است.
- Backend با FastAPI و SQLModel ساخته می‌شود.
- Frontend با React + Vite + Tailwind ساخته می‌شود.
- SQL Server لوکال استفاده می‌شود.
- Docker و Login نداریم.
- import از CSVهای جدا انجام می‌شود.
- Event Store + Current State Tables داریم.
- Warning در validation هم import را block می‌کند.
