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

## 2026-06-12 - TASK-009 Scenario و Snapshot

- مدل‌های `Scenario` و `Snapshot` اضافه شدند.
- ساخت Scenario با ارجاع اختیاری به `ImportBatch` پیاده‌سازی شد.
- fork کردن Scenario از Scenario دیگر با `parent_scenario_id` و `base_snapshot_id` پیاده‌سازی شد.
- ساخت Snapshot دستی با metadata و state ساده current state پیاده‌سازی شد.
- eventهای `ScenarioCreated`، `ScenarioForked` و `SnapshotCreated` هنگام عملیات مربوطه ثبت می‌شوند.
- replay کامل، optimizer و simulation branching engine عمداً پیاده‌سازی نشدند.

## 2026-06-12 - TASK-010 Simulation Engine حداقلی

- مدل `SimulationRun` اضافه شد.
- کنترل‌های `start`، `pause`، `resume` و `step` برای Scenario اضافه شدند.
- واحد زمان داخلی دقیقه‌ای و در `current_sim_time` ذخیره می‌شود.
- هر step event از نوع `SimulationStepped` ثبت می‌کند.
- transition ساده operation از `Queued` به `Setup`، سپس `Running` و `Finished` از مسیر event store/current state پیاده‌سازی شد.
- QC/NCR کامل، optimizer، Gantt UI و AI/ML عمداً پیاده‌سازی نشدند.

## 2026-06-12 - TASK-011 Optimizer اولیه بدون AI

- مدل‌های `OptimizationRun` و `ScheduleOperation` اضافه شدند.
- endpoint اجرای optimizer و تولید suggested schedule اضافه شد.
- heuristic ساده با priority، due time، frozen window، availability ماشین/اپراتور و material availability پیاده‌سازی شد.
- score و `changed_operations_count` برای optimization run محاسبه و ذخیره می‌شود.
- accept schedule پیاده‌سازی شد و eventهای `OperationScheduled` و `ScheduleAccepted` ثبت می‌شوند.
- AI/ML، prediction model و cost model عمداً پیاده‌سازی نشدند.

## 2026-06-12 - TASK-012 UI اولیه

- layout اصلی frontend با navigation و hash route اضافه شد.
- صفحه‌های Dashboard، Import، Scenarios، Operators، Inventory، Simulation Control و Schedule اضافه شدند.
- API client برای `GET`، `POST` و upload چندفایلی اضافه شد.
- Vite proxy برای `/api` به backend محلی تنظیم شد.
- صفحه‌ها APIهای موجود backend را در حد initial UI صدا می‌زنند.
- Gantt حرفه‌ای، drag/drop، auth/login و AI UI عمداً پیاده‌سازی نشدند.

## 2026-06-12 - TASK-013 Gantt و Drag/Drop

- کتابخانه آماده `gantt-task-react` به frontend اضافه شد.
- صفحه Schedule به نمای Gantt برای operationهای schedule تبدیل شد.
- operationها بر اساس machine timeline نمایش داده می‌شوند.
- drag/drop دستی از طریق `onDateChange` کتابخانه فعال شد.
- validation سخت‌گیرانه قبل از apply پیاده‌سازی شد و conflictها حرکت را block می‌کنند.
- دلایل conflict برای precedence، machine overlap، operator overlap، material blocker، calendar و blockerهای QC/Approval/NCR نمایش داده می‌شوند.
- Gantt سفارشی از صفر و AI alternative suggestion عمداً پیاده‌سازی نشدند.

## 2026-06-12 - TASK-014 QC/NCR/Approval

- مدل‌های `QcCheck`، `Ncr`، `NcrApproval`، `ReworkOrder` و `ReplacementOrder` اضافه شدند.
- شروع QC، ثبت نتیجه QC و تصمیم approval دستی پیاده‌سازی شد.
- QC pass وضعیت operation را از مسیر event/current state به `Finished` می‌برد.
- QC fail مسیر NCR و approval سه‌مرحله‌ای می‌سازد.
- مسیرهای fail برای rework، scrap و replacement event و artifact پایه ایجاد می‌کنند.
- AI برای NCR، cost model و approval rule engine پیچیده عمداً پیاده‌سازی نشدند.

## 2026-06-12 - TASK-015 Dashboard و Risk Rule Engine

- مدل‌های `RiskRuleSetting` و `RiskScore` اضافه شدند.
- endpointهای `/risk/settings`، `/risk/calculate/{scenario_id}` و `/risk/scores` اضافه شدند.
- تنظیمات global ریسک شامل weightهای delay، material shortage، machine failure، QC/NCR، schedule instability و thresholdهای Low/Medium/High پیاده‌سازی شد.
- اعتبارسنجی ترتیب thresholdها اضافه شد.
- محاسبه rule-based برای ریسک Operation، Order و Scenario اضافه شد.
- endpoint مدیریتی `/dashboard/manager` برای delivery، delay، production progress، capacity، bottleneck، material shortage، NCR/rework، optimizer performance و risk اضافه شد.
- صفحه Dashboard فرانت‌اند به dashboard/risk API وصل شد و امکان محاسبه ریسک و ذخیره تنظیمات ریسک از UI اضافه شد.
- AI/ML، KPI مالی و risk model پیش‌بینانه عمداً پیاده‌سازی نشدند.
