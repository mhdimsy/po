# ماژول: frontend

## هدف

ایجاد UI اولیه برای کار با قابلیت‌های backend در V1، شامل import، scenario، منابع انسانی synthetic، موجودی synthetic، simulation control، schedule ساده و dashboard مدیریتی.

## محدوده

- React + Vite + Tailwind
- route داخلی با hash route
- layout اصلی با navigation ثابت
- اتصال سبک به APIهای موجود backend
- build production با Vite

## صفحه‌ها

- Dashboard
- Import
- Scenarios
- Operators
- Inventory
- Simulation Control
- Schedule
- Gantt Schedule

## سرویس‌ها

- `apiGet`
- `apiPost`
- `apiUpload`

## endpointهای استفاده‌شده

- `GET /health`
- `POST /imports/validate`
- `POST /imports/run`
- `GET /scenarios`
- `POST /scenarios`
- `POST /scenarios/{scenario_id}/fork`
- `POST /scenarios/{scenario_id}/snapshots`
- `GET /synthetic/operators`
- `POST /synthetic/operators/generate`
- `GET /synthetic/inventory-items`
- `GET /synthetic/inventory-balances`
- `POST /synthetic/inventory/generate`
- `POST /synthetic/suppliers/generate`
- `GET /simulations/{scenario_id}/runs`
- `POST /simulations/{scenario_id}/start`
- `POST /simulations/{scenario_id}/pause`
- `POST /simulations/{scenario_id}/resume`
- `POST /simulations/{scenario_id}/step`
- `POST /optimizer/run`
- `GET /optimizer/runs`
- `GET /optimizer/runs/{optimization_run_id}/schedule`
- `POST /optimizer/runs/{optimization_run_id}/accept`

## وابستگی‌ها

- React
- Vite
- Tailwind
- React Query
- Zustand
- gantt-task-react

## محدودیت‌های فعلی

- Gantt اولیه با کتابخانه آماده پیاده‌سازی شده است، اما هنوز Gantt حرفه‌ای کامل نیست.
- drag/drop برای schedule با validation سمت UI وجود دارد.
- auth/login وجود ندارد.
- AI UI وجود ندارد.
- UI فعلاً به backend محلی از طریق Vite proxy روی `/api` وصل می‌شود.
- تست مرورگر end-to-end اجرا نشده است.

## تست‌ها

- `npm run build` موفق بود.
- TypeScript compile موفق بود.
- Vite production build موفق بود.
