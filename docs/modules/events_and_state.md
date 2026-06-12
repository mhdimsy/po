# ماژول: events_and_state

## هدف

ثبت تغییرات مهم سیستم در event store و نگهداری projectionهای current state برای خواندن سریع وضعیت فعلی سفارش، عملیات، ماشین، اپراتور و موجودی.

## محدوده

- جدول `event_store` برای ثبت eventهای دامنه‌ای.
- append service برای ثبت event جدید.
- projection ساده current state هنگام append.
- endpoint فهرست eventها.
- endpointهای فهرست current state.

## موجودیت‌ها

- `EventStore`
- `CurrentOrderState`
- `CurrentOperationState`
- `CurrentMachineState`
- `CurrentOperatorState`
- `CurrentInventoryState`

## سرویس‌ها

- `append_event`
- `apply_current_state_projection`
- `upsert_order_state`
- `upsert_operation_state`
- `upsert_machine_state`
- `upsert_operator_state`
- `upsert_inventory_state`

## endpointهای API

- `POST /events`
- `GET /events`
- `GET /events/current/orders`
- `GET /events/current/operations`
- `GET /events/current/machines`
- `GET /events/current/operators`
- `GET /events/current/inventory`

## الگوی append و current state

هر command یا تغییر مهم باید ابتدا یک event در `event_store` ثبت کند. سپس projector همان event را برای aggregateهای پشتیبانی‌شده به جدول current state متناظر اعمال می‌کند.

الگوی فعلی:

```text
Command/API
→ append_event
→ insert into event_store
→ apply_current_state_projection
→ upsert current_*_states
→ commit
```

اگر `aggregate_type` یکی از مقدارهای پشتیبانی‌شده باشد، current state به‌روزرسانی می‌شود:

- `Order` یا `ProductionOrder`
- `Operation` یا `OrderOperation` یا `RoutingOperation`
- `Machine`
- `Operator`
- `Inventory` یا `InventoryItem` یا `MaterialItem`

## eventها

نام eventها باید past-tense باشد، مثل:

- `OrderCreated`
- `OperationStarted`
- `MachineReserved`
- `OperatorReserved`
- `MaterialReserved`
- `ShortageDetected`

## جدول‌های current state

- `current_order_states`
- `current_operation_states`
- `current_machine_states`
- `current_operator_states`
- `current_inventory_states`

## وابستگی‌ها

- ماژول `database` برای SQLModel session.
- قراردادهای status از `docs/reference/DOMAIN_MODEL.md`.

## قوانین validation

- `event_type`، `aggregate_type` و `aggregate_id` الزامی هستند.
- `payload_json` اختیاری است و برای projectionهای ساده استفاده می‌شود.
- `simulation_time` اختیاری است و با واحد دقیقه ذخیره می‌شود.

## محدودیت‌های فعلی

- replay کامل پیاده‌سازی نشده است.
- simulation loop پیاده‌سازی نشده است.
- optimizer پیاده‌سازی نشده است.
- projection فعلی ساده و مستقیم است و فقط aggregateهای پایه را پوشش می‌دهد.
- اجرای واقعی روی SQL Server در این محیط تست نشده است.

## تست‌ها

- `python3 -m compileall backend/app` موفق بود.
- routeهای `/events` و `/events/current/*` ثبت شدند.
- append event روی SQLite in-memory تست شد.
- append چهار event باعث ساخت چهار event و projection برای order، operation، machine و inventory شد.
- نگاشت `OperationStarted` به status فعلی `Running` تأیید شد.
