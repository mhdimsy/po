# TASK-008: Event Store and Current State

## Goal

Event Store و Current State پایه را بساز.

## Scope

Event table fields:

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

Current State tables:

- CurrentOrderState
- CurrentOperationState
- CurrentMachineState
- CurrentOperatorState
- CurrentInventoryState

## Do not implement

- full replay
- full simulation loop
- optimizer

## Required documentation updates

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/DB_SCHEMA_CHANGE_LOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/events_and_state.md`

## Acceptance criteria

- Event append service exists.
- Event list endpoint exists.
- Basic current state update pattern is documented.
