# TASK-002: SQL Server Connection

## Goal

اتصال backend به SQL Server لوکال را پیاده کن.

## Scope

- SQLModel
- connection string از `.env`
- database session dependency
- database health endpoint
- clean error handling

## Do not implement

- master data tables
- CSV import
- simulation
- optimizer

## Endpoints

```text
GET /health
GET /health/db
```

## Required documentation updates

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/TESTING_LOG.md`
- `logs/DB_SCHEMA_CHANGE_LOG.md` if any DB artifact is added
- `docs/modules/database.md`

## Acceptance criteria

- App starts without database if only `/health` is called.
- `/health/db` reports SQL Server connection status.
- Connection string is not hardcoded.
