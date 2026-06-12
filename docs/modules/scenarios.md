# ماژول: scenarios

## هدف

مدیریت Scenario و Snapshot پایه برای پشتیبانی از fork، ثبت نقطه وضعیت و آماده‌سازی مسیر replay در تسک‌های بعدی.

## محدوده

- ساخت Scenario جدید.
- ارجاع Scenario به `ImportBatch`.
- fork کردن Scenario از Scenario دیگر.
- ساخت Snapshot دستی برای Scenario.
- ذخیره metadata و state ساده snapshot.
- فهرست کردن Scenarioها و Snapshotها.

## موجودیت‌ها

- `Scenario`
- `Snapshot`

## سرویس‌ها

- `create_scenario`
- `fork_scenario`
- `create_snapshot`
- `collect_current_state`

## endpointهای API

- `POST /scenarios`
- `GET /scenarios`
- `POST /scenarios/{scenario_id}/fork`
- `POST /scenarios/{scenario_id}/snapshots`
- `GET /scenarios/{scenario_id}/snapshots`
- `GET /scenarios/snapshots/all`

## eventها

این ماژول eventهای زیر را در `event_store` ثبت می‌کند:

- `ScenarioCreated`
- `ScenarioForked`
- `SnapshotCreated`

## جدول‌های current state

این ماژول جدول current state جدید اضافه نمی‌کند. هنگام ساخت snapshot، state فعلی از جدول‌های زیر خوانده و در `snapshots.state_json` ذخیره می‌شود:

- `current_order_states`
- `current_operation_states`
- `current_machine_states`
- `current_operator_states`
- `current_inventory_states`

## وابستگی‌ها

- `import_batches` برای `base_import_batch_id`.
- ماژول `events_and_state` برای ثبت event و خواندن current state.
- ماژول `database` برای SQLModel session.

## قوانین validation

- نام Scenario الزامی است.
- fork فقط از Scenario موجود انجام می‌شود.
- snapshot فقط برای Scenario موجود ساخته می‌شود.
- `settings_json` و `metadata_json` باید JSON-compatible باشند.

## محدودیت‌های فعلی

- replay کامل پیاده‌سازی نشده است.
- simulation branching engine پیاده‌سازی نشده است.
- optimizer پیاده‌سازی نشده است.
- snapshot فعلی فقط state جدول‌های current state پایه را ذخیره می‌کند.
- کپی کردن state به Scenario فرزند هنگام fork انجام نمی‌شود؛ فقط رابطه parent و base snapshot ثبت می‌شود.
- اجرای واقعی روی SQL Server در این محیط تست نشده است.

## تست‌ها

- `python3 -m compileall backend/app` موفق بود.
- routeهای `/scenarios/*` ثبت شدند.
- ساخت Scenario با ارجاع به `ImportBatch` روی SQLite in-memory موفق بود.
- ساخت Snapshot دستی با یک current order state موفق بود.
- fork کردن Scenario از Snapshot موفق بود.
- eventهای `ScenarioCreated`، `SnapshotCreated` و `ScenarioForked` ثبت شدند.
