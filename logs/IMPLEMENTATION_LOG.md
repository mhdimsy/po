# لاگ پیاده‌سازی

## 2026-06-12 - TASK-001 اسکلت پروژه

- ساختار اولیه backend با FastAPI زیر `backend/app` ساخته شد.
- ساختار اولیه frontend با React/Vite/Tailwind زیر `frontend` ساخته شد.
- دستورهای اجرای محلی به `README.md` اضافه شد.
- placeholderهای ماژولی برای modular monolith برنامه‌ریزی‌شده اضافه شد.
- در این تسک، عمداً اتصال SQL Server، مدل‌ها، import، simulation، optimizer، auth و Docker اضافه نشد.

## 2026-06-12 - TASK-002 اتصال SQL Server

- مدیریت اتصال SQL Server مبتنی بر environment در `backend/app/core/db.py` اضافه شد.
- `GET /health/db` اضافه شد.
- dependency مربوط به database session و مدیریت خطای runtime اضافه شد.
- `GET /health` مستقل از تنظیم دیتابیس نگه داشته شد.
- جدول دامنه‌ای خارج از محدوده مدل‌های تسک‌های بعدی اضافه نشد.

## 2026-06-12 - TASK-003 مدل‌های Master Data

- موجودیت‌های SQLModel برای import batchها، metadata مربوط به validation، BOM، سفارش‌ها، routingها، processها، machineها، work centerها و capabilityهای machine-process اضافه شد.
- endpointهای read-only برای master data اضافه شد.
- `POST /master-data/schema/create` به‌عنوان روش ساخت schema در نمونه محلی اضافه شد.
- رابطه‌ها از طریق source ID fieldها و ارجاع به import batch مستند شدند.

## 2026-06-12 - TASK-004 اعتبارسنجی CSV بدون import

- endpoint مربوط به validate-only برای CSVهای multipart در `POST /imports/validate` اضافه شد.
- بررسی فایل/ستون الزامی، typeهای پایه، کلید تکراری، FK و warningهای blocker پیاده‌سازی شد.
- تأیید شد که validate-only هیچ insert در دیتابیس انجام نمی‌دهد.

## 2026-06-12 - TASK-005 ورود CSV با ImportBatch

- `POST /imports/run` اضافه شد.
- رفتار validation-before-import پیاده‌سازی شد.
- ساخت `ImportBatch` و insert در جدول‌های master فقط وقتی validation هیچ error یا warning ندارد اضافه شد.
- شمارش ردیف‌های واردشده به تفکیک فایل و شمارش موجودیت‌های ساخته‌شده اضافه شد.
- UI، scenario migration، simulation و optimizer عمداً پیاده‌سازی نشدند.

## 2026-06-12 - TASK-006 منابع انسانی synthetic

- مدل‌های `Operator`، `Skill`، `OperatorSkill`، `Shift`، `WorkCenterShiftRule` و `OperatorAvailability` اضافه شدند.
- سرویس generator برای تولید اپراتورهای synthetic با مقدار پیش‌فرض ۵۰۰ نفر اضافه شد.
- توزیع پیشنهادی اپراتورها بر اساس WorkCenter و تعداد Machineها پیاده‌سازی شد.
- نسبت multi-skill قابل تنظیم شد و سطح مهارت‌ها به‌صورت تصادفی در بازه ۱ تا ۵ تولید می‌شود.
- endpointهای تولید و list برای اپراتورها، skillها و shiftها اضافه شدند.
- optimizer assignment logic، fatigue model، auth/user و UI عمداً پیاده‌سازی نشدند.

## 2026-06-12 - TASK-007 موجودی و Supplier synthetic

- مدل‌های `Warehouse`، `InventoryItem`، `InventoryBalance`، `Supplier`، `BOMItemSupplier` و `PurchaseRequest` اضافه شدند.
- generator موجودی با presetهای `Plenty`، `Normal`، `Shortage-heavy` و `Random Chaos` اضافه شد.
- generator supplier با presetهای `Reliable`، `Mixed`، `Unreliable` و `Fast but Expensive` اضافه شد.
- نگاشت چند supplier برای هر BOM item و یک default supplier برای هر item پیاده‌سازی شد.
- برای کمبود موجودی نسبت به safety stock، `PurchaseRequest` بدون supplier انتخاب‌شده ساخته می‌شود.
- material cost، انتخاب خودکار supplier، integration خرید واقعی و UI عمداً پیاده‌سازی نشدند.

## 2026-06-12 - TASK-008 Event Store و Current State

- مدل `EventStore` با فیلدهای `event_id`، `event_type`، `aggregate_type`، `aggregate_id`، `scenario_id`، `payload_json`، `simulation_time` و `created_at` اضافه شد.
- جدول‌های `CurrentOrderState`، `CurrentOperationState`، `CurrentMachineState`، `CurrentOperatorState` و `CurrentInventoryState` اضافه شدند.
- سرویس `append_event` برای ثبت event و اجرای projection ساده current state اضافه شد.
- endpointهای `POST /events`، `GET /events` و `GET /events/current/*` اضافه شدند.
- replay کامل، simulation loop و optimizer عمداً پیاده‌سازی نشدند.
