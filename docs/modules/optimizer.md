# ماژول: optimizer

## هدف

تولید schedule پیشنهادی اولیه بدون AI/ML، با heuristic ساده و بررسی constraintهای پایه برای operationهای موجود در current state.

## محدوده

- اجرای optimizer به‌صورت دستی از API.
- تولید suggested schedule برای operationهای قابل زمان‌بندی.
- در نظر گرفتن precedence ساده بر اساس ترتیب operationهای یک order.
- در نظر گرفتن availability ساده machine و operator.
- بررسی material availability وقتی payload operation شامل `required_inventory_item_id` و `required_qty` باشد.
- در نظر گرفتن `priority`/`priority_score` و `due_time` از payload.
- ذخیره optimization run و schedule operationها.
- accept کردن schedule پیشنهادی.

## موجودیت‌ها

- `OptimizationRun`
- `ScheduleOperation`

## سرویس‌ها

- `run_optimizer`
- `accept_schedule`
- `list_optimizer_runs`
- `list_schedule`

## endpointهای API

- `POST /optimizer/run`
- `GET /optimizer/runs`
- `GET /optimizer/runs/{optimization_run_id}/schedule`
- `POST /optimizer/runs/{optimization_run_id}/accept`

## eventها

این ماژول eventهای زیر را ثبت می‌کند:

- `ScheduleSuggested`
- `OperationScheduled`
- `ScheduleAccepted`

## جدول‌های current state

optimizer مستقیماً جدول current state جدید اضافه نمی‌کند. هنگام accept، eventهای `OperationScheduled` باعث به‌روزرسانی `current_operation_states` می‌شوند.

## الگوریتم فعلی

الگوریتم فعلی deterministic و heuristic است:

```text
1. operationهای قابل زمان‌بندی از current_operation_states خوانده می‌شوند.
2. operationها بر اساس priority، due_time و operation_sequence مرتب می‌شوند.
3. machine و operator موجود انتخاب می‌شوند.
4. start_time با frozen_window، availability منابع و ترتیب operationهای همان order تنظیم می‌شود.
5. material availability ساده بررسی می‌شود.
6. schedule پیشنهادی ذخیره می‌شود.
7. score و changed_operations_count محاسبه می‌شود.
```

## وابستگی‌ها

- `scenarios`
- `events_and_state`
- `current_operation_states`
- `current_machine_states`
- `current_operator_states`
- `current_inventory_states`

## قوانین validation

- `scenario_id` الزامی است.
- `frozen_window_minutes` باید صفر یا بیشتر باشد.
- `horizon_minutes` باید بزرگ‌تر از صفر باشد.
- AI/ML، prediction model و cost model در V1 استفاده نمی‌شوند.

## محدودیت‌های فعلی

- constraint optimization کامل پیاده‌سازی نشده است.
- machine capability و operator authorization واقعی هنوز از master data خوانده نمی‌شوند.
- calendar/shift handling ساده است و فقط availability فعلی منابع در نظر گرفته می‌شود.
- QC/approval/NCR blocking هنوز بررسی نمی‌شود.
- cost model عمداً وجود ندارد.
- اجرای واقعی روی SQL Server در این محیط تست نشده است.

## تست‌ها

- `python3 -m compileall backend/app` موفق بود.
- routeهای `/optimizer/*` ثبت شدند.
- تست SQLite in-memory با یک Scenario، دو operation، یک machine، یک operator و یک inventory state موفق بود.
- optimizer تعداد ۲ schedule operation ساخت.
- run شامل score و `changed_operations_count` بود.
- accept schedule تعداد ۲ operation را پذیرفت و eventهای `OperationScheduled` و `ScheduleAccepted` ثبت شدند.
