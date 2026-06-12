# وضعیت پروژه

## وضعیت فعلی

زیرساخت پروژه، لایه اتصال SQL Server، مدل‌های master data، validate-only برای CSV، import CSV همراه با `ImportBatch`، generator منابع انسانی synthetic، generator موجودی/supplier synthetic و event store/current state پایه پیاده‌سازی شده‌اند.

## تسک جاری

TASK-008 تکمیل شده است.

## تسک‌های انجام‌شده

- `TASK-001-project-skeleton.md`
- `TASK-002-sqlserver-connection.md`
- `TASK-003-master-data-models.md`
- `TASK-004-csv-validate-only.md`
- `TASK-005-csv-import-with-import-batch.md`
- `TASK-006-synthetic-human-resources.md`
- `TASK-007-synthetic-inventory-and-suppliers.md`
- `TASK-008-event-store-current-state.md`

## تسک بعدی پیشنهادی

`TASK-009-scenario-and-snapshot.md`

## تصمیم‌های مهم فعال

- V1 بدون AI/ML واقعی است.
- Backend با FastAPI و SQLModel ساخته می‌شود.
- Frontend با React + Vite + Tailwind ساخته می‌شود.
- SQL Server لوکال استفاده می‌شود.
- Docker و Login نداریم.
- import از CSVهای جدا انجام می‌شود.
- Event Store + Current State Tables داریم.
- Warning در validation هم import را block می‌کند.
