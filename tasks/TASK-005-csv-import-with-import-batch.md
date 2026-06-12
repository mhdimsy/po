# TASK-005: CSV Import with ImportBatch

## Goal

بعد از Validate Only، import واقعی را پیاده کن.

## Scope

- create ImportBatch
- insert validated CSV rows into master tables
- versioned import
- report imported row counts
- block import if any error/warning exists

## Do not implement

- UI
- scenario migration
- simulation
- optimizer

## Required documentation updates

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/DB_SCHEMA_CHANGE_LOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/import_factory.md`
- `docs/api/import_factory.md`

## Acceptance criteria

- Import creates a new ImportBatch.
- Imported records reference ImportBatch.
- Import fails if validation has warnings/errors.
