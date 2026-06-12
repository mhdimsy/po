# TASK-013: Gantt and Drag/Drop

## Goal

گانت چارت را با کتابخانه آماده React اضافه کن.

## Scope

- show operations by machine
- show current schedule
- show suggested schedule
- drag/drop manual move
- strict validation before apply
- conflicts block apply
- conflict reasons shown

## Validation must check

- operation precedence
- machine availability/status
- operator eligibility/availability
- material availability
- calendar
- QC/Approval/NCR blockers if available

## Do not implement

- custom Canvas/SVG Gantt from scratch
- AI alternative suggestions

## Required documentation updates

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/gantt.md`

## Acceptance criteria

- Gantt renders schedule.
- Drag/drop calls validation.
- Invalid move is blocked with reasons.
