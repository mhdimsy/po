# ماژول: database

## هدف

فراهم کردن تنظیم اتصال SQL Server، گزارش سلامت دیتابیس، و پشتیبانی از ساخت schema برای جدول‌های SQLModel.

## محدوده

- خواندن connection string از `SQLSERVER_CONNECTION_STRING` یا `DATABASE_URL`.
- مستقل نگه داشتن `/health` از در دسترس بودن دیتابیس.
- افزودن `/health/db` برای گزارش وضعیت اتصال SQL Server.
- افزودن endpoint ساخت schema برای محیط توسعه.

## موجودیت‌ها

این ماژول مالک موجودیت دامنه‌ای نیست.

## سرویس‌ها

- `get_engine`
- `get_session`
- `create_db_and_tables`
- `check_database_connection`

## endpointهای API

- `GET /health/db`
- `POST /master-data/schema/create`

## eventها

ندارد.

## جدول‌های current state

ندارد.

## وابستگی‌ها

- SQLModel
- SQLAlchemy
- pyodbc از مسیر connection stringهای SQL Server در SQLAlchemy

## قوانین validation

- connection string باید از environment variable خوانده شود و نباید hardcode شود.

## محدودیت‌های فعلی

- هنوز migration framework اضافه نشده است.
- اتصال واقعی به SQL Server در این محیط تست نشده است.

## تست‌ها

- تست مستقیم تابع health دیتابیس، بدون تنظیم connection string، مقدار `not_configured` برگرداند.
