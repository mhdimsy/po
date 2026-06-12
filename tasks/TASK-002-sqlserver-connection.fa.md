# TASK-002: اتصال SQL Server

## هدف

اتصال backend به SQL Server لوکال را پیاده کن.

## محدوده

- استفاده از SQLModel
- خواندن connection string از `.env`
- dependency برای database session
- endpoint سلامت دیتابیس
- مدیریت خطای تمیز

## پیاده‌سازی نکن

- جدول‌های master data
- import فایل CSV
- simulation
- optimizer

## endpointها

```text
GET /health
GET /health/db
```

## مستندات الزامی بعد از اجرا

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/TESTING_LOG.md`
- `logs/DB_SCHEMA_CHANGE_LOG.md` اگر artifact مربوط به دیتابیس اضافه شد
- `docs/modules/database.md`

## معیار پذیرش

- اگر فقط `/health` صدا زده شود، app بدون دیتابیس هم start شود.
- `/health/db` وضعیت اتصال SQL Server را گزارش کند.
- connection string hardcode نشده باشد.
