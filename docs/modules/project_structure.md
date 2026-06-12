# ماژول: project_structure

## هدف

تعریف ساختار اولیه repo برای توسعه backend و frontend با معماری modular monolith.

## محدوده

- اسکلت اولیه backend با FastAPI.
- اسکلت اولیه frontend با React/Vite/Tailwind.
- پوشه‌های ماژولی برای bounded contextهای برنامه‌ریزی‌شده V1.
- دستورهای اجرای محلی در README.

## موجودیت‌ها

ندارد.

## سرویس‌ها

- ساخت app در `backend/app/main.py`.
- router ساده health در `backend/app/health.py`.

## endpointهای API

- `GET /health`

## eventها

ندارد.

## جدول‌های current state

ندارد.

## وابستگی‌ها

- Backend: FastAPI, Uvicorn, SQLModel, pyodbc, python-multipart.
- Frontend: React, Vite, Tailwind, React Query, Zustand.

## قوانین validation

ندارد.

## محدودیت‌های فعلی

- صفحه‌های frontend فعلاً placeholder هستند.
- هیچ workflow دامنه‌ای در اسکلت اولیه پیاده‌سازی نشده است.

## تست‌ها

- `python3 -m compileall backend/app`
- `npm run build`
