# TASK-010: Minimal Simulation Engine

## Goal

simulation engine حداقلی را بساز.

## Scope

- internal time unit: minute
- start / pause / resume / step
- event-based core ساده
- tick only for state refresh
- operation statuses:
  - Queued
  - WaitingMaterial
  - WaitingMachine
  - WaitingOperator
  - Setup
  - Running
  - Finished
  - Blocked

## Do not implement

- full QC/NCR
- full optimizer
- Gantt UI
- AI/ML

## Required documentation updates

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/simulation.md`

## Acceptance criteria

- Can step simulation time.
- State changes create events.
- Current state tables update.
