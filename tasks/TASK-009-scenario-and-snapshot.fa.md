# TASK-009: Scenario و Snapshot

## هدف

Scenario و Snapshot پایه را پیاده کن.

## محدوده

- موجودیت Scenario
- ارجاع Scenario به ImportBatch
- قابلیت fork شدن Scenario از Scenario دیگر
- موجودیت Snapshot
- ساخت Snapshot دستی
- metadata مربوط به Snapshot

## پیاده‌سازی نکن

- replay کامل
- optimizer
- simulation branching engine

## مستندات الزامی بعد از اجرا

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/DB_SCHEMA_CHANGE_LOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/scenarios.md`

## معیار پذیرش

- Scenario ساخته شود.
- Scenario fork شود.
- Snapshot ساخته شود.
- Scenarioها و Snapshotها قابل list شدن باشند.
