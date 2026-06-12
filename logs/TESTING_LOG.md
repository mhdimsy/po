# لاگ تست

## 2026-06-12

- `python3 -m compileall backend/app` موفق بود.
- ثبت routeهای backend app با dependencyهای موقت از `/tmp/jobshop6-pydeps` با موفقیت load شد.
- health check مستقیم مقدار `{"status": "ok"}` و وضعیت دیتابیس `not_configured` را بدون connection string برگرداند.
- validation فایل‌های CSV در حالت نبود فایل‌ها، issueهای blocker از نوع `MISSING_FILE` برگرداند.
- مجموعه CSV حداقلی در حافظه مقدار `import_ready=True` و صفر issue برگرداند.
- import روی SQLite in-memory یک `ImportBatch` ساخت و ردیف‌های master data را درج کرد.
- `npm run build` برای frontend موفق بود.
- Uvicorn startup روی `http://127.0.0.1:8000` را گزارش کرد.
- Vite startup روی `http://127.0.0.1:5173/` را گزارش کرد.

یادداشت‌های محیطی:

- دستور `python` در دسترس نبود؛ از `python3` استفاده شد.
- `python3 -m venv` به‌دلیل نصب نبودن `python3-venv`/`ensurepip` روی سیستم شکست خورد.
- dependencyهای backend برای verification به‌صورت موقت در `/tmp/jobshop6-pydeps` نصب شدند.
- تست health مبتنی بر TestClient بعد از hang شدن متوقف شد؛ به‌جای آن از تست مستقیم تابع‌ها و load شدن routeهای app استفاده شد.
- `curl http://127.0.0.1:8000/health` از یک exec جدا، با وجود خروجی startup از uvicorn، connection refused برگرداند.

## 2026-06-12 - TASK-006

- `python3 -m compileall backend/app` موفق بود.
- load شدن app و ثبت routeهای `/synthetic/operators/generate`، `/synthetic/operators`، `/synthetic/skills` و `/synthetic/shifts` موفق بود.
- generator روی SQLite in-memory با ۲ WorkCenter، ۳ Machine و ۲ Process تست شد.
- تولید ۲۰ اپراتور با `multi_skill_ratio=0.5` موفق بود.
- در تست، ۲۰ ردیف `Operator`، ۳۳ ردیف `OperatorSkill` و توزیع ۱۳/۷ بین WorkCenterها ساخته شد.
- مقدارهای skill level در تست بین ۱ و ۵ بود.
- تست جداگانه تولید پیش‌فرض بدون master data انجام شد و ۵۰۰ ردیف `Operator` با distribution total برابر ۵۰۰ ساخت.

## 2026-06-12 - TASK-007

- `python3 -m compileall backend/app` موفق بود.
- load شدن app و ثبت routeهای `/synthetic/inventory/generate`، `/synthetic/suppliers/generate`، `/synthetic/inventory-items`، `/synthetic/inventory-balances`، `/synthetic/suppliers`، `/synthetic/bom-item-suppliers` و `/synthetic/purchase-requests` موفق بود.
- generator روی SQLite in-memory با ۳ BOM item و ۱ BOMPart تست شد.
- preset موجودی `Shortage-heavy` تعداد ۳ `InventoryItem` و ۳ `InventoryBalance` ساخت.
- preset supplier `Reliable` با `suppliers_per_item=2` تعداد ۲ supplier و ۶ mapping ساخت.
- برای هر inventory item دقیقاً یک default supplier در mappingها وجود داشت.
- تعداد ۳ `PurchaseRequest` بدون انتخاب supplier برای کمبودهای synthetic ساخته شد.

## 2026-06-12 - TASK-008

- `python3 -m compileall backend/app` موفق بود.
- load شدن app و ثبت routeهای `/events` و `/events/current/orders`، `/events/current/operations`، `/events/current/machines`، `/events/current/operators` و `/events/current/inventory` موفق بود.
- append event روی SQLite in-memory تست شد.
- ثبت ۴ event برای aggregateهای order، operation، machine و inventory موفق بود.
- projectionهای current state برای order، operation، machine و inventory ساخته شدند.
- نگاشت `OperationStarted` به status فعلی `Running` تأیید شد.
