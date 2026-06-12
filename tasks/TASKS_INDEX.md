# Tasks Index

قانون: هر بار فقط یک تسک اجرا شود.

## Phase 0 - Project Foundation

1. `TASK-001-project-skeleton.md`
2. `TASK-002-sqlserver-connection.md`
3. `TASK-003-master-data-models.md`

## Phase 1 - CSV Import

4. `TASK-004-csv-validate-only.md`
5. `TASK-005-csv-import-with-import-batch.md`

## Phase 2 - Synthetic Data

6. `TASK-006-synthetic-human-resources.md`
7. `TASK-007-synthetic-inventory-and-suppliers.md`

## Phase 3 - Event, Scenario, State

8. `TASK-008-event-store-current-state.md`
9. `TASK-009-scenario-and-snapshot.md`

## Phase 4 - Simulation and Optimizer

10. `TASK-010-minimal-simulation-engine.md`
11. `TASK-011-initial-optimizer-no-ai.md`

## Phase 5 - UI

12. `TASK-012-initial-ui.md`
13. `TASK-013-gantt-and-drag-drop.md`

## Phase 6 - Production Complexity

14. `TASK-014-qc-ncr-approval.md`
15. `TASK-015-dashboard-and-risk-engine.md`

## Documentation rule for every task

بعد از هر تسک، این‌ها باید آپدیت شوند:

```text
logs/IMPLEMENTATION_LOG.md
logs/CHANGELOG.md
logs/TESTING_LOG.md
docs/PROJECT_STATUS.md
```

اگر دیتابیس تغییر کرد:

```text
logs/DB_SCHEMA_CHANGE_LOG.md
```

اگر ابهام یا نقصی پیدا شد:

```text
logs/OPEN_QUESTIONS.md
logs/KNOWN_ISSUES.md
```
