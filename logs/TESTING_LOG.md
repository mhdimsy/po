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

## 2026-06-12 - TASK-009

- `python3 -m compileall backend/app` موفق بود.
- load شدن app و ثبت routeهای `/scenarios`، `/scenarios/{scenario_id}/fork`، `/scenarios/{scenario_id}/snapshots` و `/scenarios/snapshots/all` موفق بود.
- ساخت Scenario با ارجاع به `ImportBatch` روی SQLite in-memory موفق بود.
- ساخت Snapshot دستی برای Scenario با یک current order state موفق بود.
- fork کردن Scenario از Snapshot موفق بود.
- بعد از create/fork/snapshot تعداد ۲ Scenario، ۱ Snapshot و ۳ Event ثبت شد.
- eventهای ثبت‌شده شامل `ScenarioCreated`، `SnapshotCreated` و `ScenarioForked` بودند.

## 2026-06-12 - TASK-010

- `python3 -m compileall backend/app` موفق بود.
- load شدن app و ثبت routeهای `/simulations/{scenario_id}/start`، `/pause`، `/resume`، `/step` و `/runs` موفق بود.
- تست SQLite in-memory با یک Scenario و یک operation با وضعیت `Queued` انجام شد.
- start، pause، resume و سه step اجرا شدند.
- زمان simulation از ۰ به ۳ دقیقه رسید.
- وضعیت operation در سه step از `Queued` به `Setup`، سپس `Running` و سپس `Finished` تغییر کرد.
- تعداد ۱۱ event شامل `SimulationStarted`، `SimulationPaused`، `SimulationResumed`، `SimulationStepped`، `OperationSetup`، `OperationStarted` و `OperationFinished` ثبت شد.

## 2026-06-12 - TASK-011

- `python3 -m compileall backend/app` موفق بود.
- load شدن app و ثبت routeهای `/optimizer/run`، `/optimizer/runs`، `/optimizer/runs/{optimization_run_id}/schedule` و `/optimizer/runs/{optimization_run_id}/accept` موفق بود.
- تست SQLite in-memory با یک Scenario، دو operation، یک machine، یک operator و یک inventory state انجام شد.
- optimizer تعداد ۲ `ScheduleOperation` ساخت.
- `OptimizationRun` دارای score برابر `140.0` و `changed_operations_count=2` بود.
- accept schedule تعداد ۲ operation را پذیرفت.
- eventهای `ScheduleSuggested`، دو event `OperationScheduled` و `ScheduleAccepted` ثبت شدند.

## 2026-06-12 - TASK-012

- `npm run build` در `frontend` موفق بود.
- TypeScript compile موفق بود.
- Vite production build موفق بود.
- خروجی build شامل bundleهای CSS و JS تولید شد.

## 2026-06-12 - TASK-013

- `npm install gantt-task-react --legacy-peer-deps` موفق بود.
- `npm run build` در `frontend` موفق بود.
- TypeScript compile موفق بود.
- Vite production build موفق بود.
- Rollup درباره comment داخلی کتابخانه `gantt-task-react` هشدار داد ولی build را کامل کرد.

## 2026-06-12 - TASK-014

- `python3 -m compileall backend/app` موفق بود.
- load شدن app و ثبت routeهای `/qc-ncr/checks`، `/qc-ncr/checks/{qc_check_id}/result`، `/qc-ncr/ncrs`، `/qc-ncr/approvals` و `/qc-ncr/approvals/{approval_id}/decision` موفق بود.
- تست SQLite in-memory برای QC pass موفق بود و operation به `Finished` رفت.
- تست SQLite in-memory برای QC fail با disposition `SimpleRework` موفق بود.
- یک NCR، سه approval step و یک `ReworkOrder` ساخته شد.
- بعد از approve شدن هر سه approval، operation مرتبط به `Rework` رفت.
- eventهای `QCStarted`، `QCPassed`، `QCFailed`، `NCROpened`، `NCRApprovalRequested`، `NCRApproved`، `NCRDispositionDecided` و `ReworkCreated` ثبت شدند.

## 2026-06-12 - TASK-015

- `python3 -m compileall backend/app` موفق بود.
- load شدن app و ثبت routeهای `/risk/settings`، `/risk/calculate/{scenario_id}`، `/risk/scores` و `/dashboard/manager` موفق بود.
- تست SQLite in-memory برای Risk Rule Engine و Dashboard اجرا شد.
- خواندن تنظیمات پیش‌فرض ریسک موفق بود.
- به‌روزرسانی `delay_risk_weight` و `high_threshold` موفق بود.
- validation ترتیب thresholdها با ورودی نامعتبر تست شد و خطا برگرداند.
- محاسبه ریسک برای یک Scenario نمونه ۴ score شامل Operation، Order و Scenario ساخت.
- داشبورد نمونه مقدارهای delivery، material shortage، NCR/rework و optimizer performance را درست aggregate کرد.
- `npm run build` در `frontend` موفق بود.
- TypeScript compile موفق بود.
- Vite production build موفق بود.
- Rollup همچنان درباره comment داخلی کتابخانه `gantt-task-react` هشدار داد ولی build را کامل کرد.
