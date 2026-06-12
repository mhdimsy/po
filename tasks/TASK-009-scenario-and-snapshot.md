# TASK-009: Scenario and Snapshot

## Goal

Scenario و Snapshot پایه را پیاده کن.

## Scope

- Scenario entity
- Scenario references ImportBatch
- Scenario can fork from another Scenario
- Snapshot entity
- manual snapshot creation
- snapshot metadata

## Do not implement

- full replay
- optimizer
- simulation branching engine

## Required documentation updates

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/DB_SCHEMA_CHANGE_LOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/scenarios.md`

## Acceptance criteria

- Create scenario.
- Fork scenario.
- Create snapshot.
- List scenarios/snapshots.
