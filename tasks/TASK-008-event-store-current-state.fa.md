# TASK-008: Event Store و Current State

## هدف

Event Store و Current State پایه را بساز.

## محدوده

فیلدهای جدول event:

```text
event_id
event_type
aggregate_type
aggregate_id
scenario_id
payload_json
simulation_time
created_at
```

جدول‌های Current State:

- CurrentOrderState
- CurrentOperationState
- CurrentMachineState
- CurrentOperatorState
- CurrentInventoryState

## پیاده‌سازی نکن

- replay کامل
- simulation loop کامل
- optimizer

## مستندات الزامی بعد از اجرا

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/DB_SCHEMA_CHANGE_LOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/events_and_state.md`

## معیار پذیرش

- سرویس append event وجود داشته باشد.
- endpoint فهرست eventها وجود داشته باشد.
- الگوی پایه update کردن current state مستند شده باشد.
