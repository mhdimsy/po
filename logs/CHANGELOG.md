# تغییرات

## 2026-06-12

- اسکلت backend با FastAPI و endpointهای health اضافه شد.
- تنظیم اتصال SQL Server از طریق environment variable اضافه شد.
- جدول‌های master data با SQLModel و endpointهای read اضافه شد.
- endpoint مخصوص validate-only برای CSV اضافه شد.
- endpoint import CSV همراه با `ImportBatch` اضافه شد.
- اسکلت frontend با React/Vite/Tailwind اضافه شد.
- مستندات ماژولی و API برای ساختار پروژه، دیتابیس، master data و import factory اضافه شد.
- generator منابع انسانی synthetic با endpointهای `/synthetic/operators/generate`، `/synthetic/operators`، `/synthetic/skills` و `/synthetic/shifts` اضافه شد.
- generator موجودی و supplier synthetic با endpointهای `/synthetic/inventory/generate`، `/synthetic/suppliers/generate` و list endpointهای مرتبط اضافه شد.
- event store و current state پایه با endpointهای `/events` و `/events/current/*` اضافه شد.
- Scenario و Snapshot پایه با endpointهای `/scenarios`، `/scenarios/{scenario_id}/fork` و `/scenarios/{scenario_id}/snapshots` اضافه شد.
- simulation engine حداقلی با endpointهای `/simulations/{scenario_id}/start`، `/pause`، `/resume`، `/step` و `/runs` اضافه شد.
- optimizer اولیه بدون AI با endpointهای `/optimizer/run`، `/optimizer/runs`، `/optimizer/runs/{id}/schedule` و `/optimizer/runs/{id}/accept` اضافه شد.
- UI اولیه با صفحه‌های Import، Scenario، Operators، Inventory، Simulation Control، Schedule و Dashboard اضافه شد.
- Gantt آماده React و drag/drop همراه با validation conflict به صفحه Schedule اضافه شد.
- QC/NCR/Approval پایه با endpointهای `/qc-ncr/*` اضافه شد.
- Risk Rule Engine بدون AI با endpointهای `/risk/settings`، `/risk/calculate/{scenario_id}` و `/risk/scores` اضافه شد.
- داشبورد مدیریتی aggregate با endpoint `/dashboard/manager` اضافه شد.
- صفحه Dashboard برای نمایش KPIهای مدیریتی، scoreهای ریسک و تنظیمات ریسک به‌روزرسانی شد.
