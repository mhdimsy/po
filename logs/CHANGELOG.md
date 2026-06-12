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
