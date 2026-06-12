# TASK-001: اسکلت پروژه

## هدف

اسکلت اولیه repo را بساز.

## محدوده

- Backend با FastAPI
- Frontend با React + Vite + Tailwind
- ساختار modular monolith
- بدون Docker
- بدون Login
- بدون domain logic
- health check ساده backend
- صفحه ساده frontend

## پیاده‌سازی نکن

- اتصال SQL Server
- مدل‌های دیتابیس
- import
- simulation
- optimizer
- auth
- Docker

## ساختار مورد انتظار

```text
backend/
  app/
    main.py
    core/
    modules/
    shared/
  pyproject.toml or requirements.txt
frontend/
  src/
  package.json
  vite.config.*
docs/
logs/
tasks/
```

## مستندات الزامی بعد از اجرا

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/TESTING_LOG.md`
- `docs/PROJECT_STATUS.md`
- ساخت `docs/modules/project_structure.md`

## معیار پذیرش

- Backend به‌صورت محلی اجرا شود.
- `GET /health` مقدار OK برگرداند.
- Frontend به‌صورت محلی اجرا شود.
- README شامل دستورهای اجرای محلی باشد.
