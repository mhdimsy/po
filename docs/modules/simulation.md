# ماژول: simulation

## هدف

پیاده‌سازی engine حداقلی شبیه‌سازی برای کنترل زمان داخلی، start/pause/resume/step و اعمال تغییر وضعیت ساده operationها از مسیر event store و current state.

## محدوده

- واحد زمان داخلی دقیقه است.
- ساخت و نگهداری `SimulationRun`.
- کنترل‌های `start`، `pause`، `resume` و `step`.
- ثبت event برای تغییرات simulation و operation.
- به‌روزرسانی current state از طریق event projection موجود.
- transition ساده operation در هر step.

## موجودیت‌ها

- `SimulationRun`

## سرویس‌ها

- `start_simulation`
- `pause_simulation`
- `resume_simulation`
- `step_simulation`
- `transition_one_operation`
- `list_simulation_runs`

## endpointهای API

- `POST /simulations/{scenario_id}/start`
- `POST /simulations/{scenario_id}/pause`
- `POST /simulations/{scenario_id}/resume`
- `POST /simulations/{scenario_id}/step`
- `GET /simulations/{scenario_id}/runs`

## eventها

این ماژول eventهای زیر را ثبت می‌کند:

- `SimulationStarted`
- `SimulationPaused`
- `SimulationResumed`
- `SimulationStepped`
- `OperationSetup`
- `OperationStarted`
- `OperationFinished`
- `OperationBlocked`

## جدول‌های current state

خود ماژول simulation جدول current state جدید اضافه نمی‌کند. تغییرات operation از طریق eventهای `Operation*` به `current_operation_states` اعمال می‌شود.

## الگوی transition فعلی

در هر step، اگر `process_one_operation=true` باشد، اولین operation مربوط به scenario که status قابل پردازش دارد انتخاب می‌شود:

```text
Queued -> Setup
Setup -> Running
Running -> Finished
WaitingMaterial -> Blocked
WaitingMachine -> Blocked
WaitingOperator -> Blocked
```

## وابستگی‌ها

- `scenarios` برای وجود Scenario.
- `events_and_state` برای ثبت event و به‌روزرسانی current state.

## قوانین validation

- `speed_factor` باید بیشتر از ۰ و حداکثر ۱۰۰ باشد.
- `start_time` باید صفر یا بیشتر باشد.
- `minutes` در step باید بین ۱ و ۱۰۰۸۰ باشد.
- start روی Scenario ناموجود خطا می‌دهد.
- pause/resume/step به simulation run فعال نیاز دارد.

## محدودیت‌های فعلی

- full QC/NCR پیاده‌سازی نشده است.
- optimizer پیاده‌سازی نشده است.
- Gantt UI پیاده‌سازی نشده است.
- AI/ML پیاده‌سازی نشده است.
- calendar، material availability، machine capability و operator authorization در start conditionهای واقعی هنوز بررسی نمی‌شوند.
- اجرای واقعی روی SQL Server در این محیط تست نشده است.

## تست‌ها

- `python3 -m compileall backend/app` موفق بود.
- routeهای `/simulations/{scenario_id}/*` ثبت شدند.
- تست SQLite in-memory با یک Scenario و یک operation queued موفق بود.
- start/pause/resume/step اجرا شد.
- پس از سه step، زمان simulation به ۳ دقیقه رسید.
- وضعیت operation از `Queued` به `Setup`، سپس `Running` و در نهایت `Finished` تغییر کرد.
- eventهای simulation و operation در `event_store` ثبت شدند.
