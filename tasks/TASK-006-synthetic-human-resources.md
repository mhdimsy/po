# TASK-006: Synthetic Human Resources

## Goal

generator نیروی انسانی synthetic را بساز.

## Scope

- generate configurable number of operators, default 500
- distribution suggestion based on WorkCenter/Machine data
- random skill level 1..5
- configurable multi-skill ratio
- shifts configurable by WorkCenter
- save generated operators/skills/shifts to DB

## Entities

- Operator
- Skill
- OperatorSkill
- Shift
- WorkCenterShiftRule
- OperatorAvailability

## Do not implement

- optimizer assignment logic
- fatigue model
- auth/users
- UI unless explicitly requested

## Required documentation updates

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/DB_SCHEMA_CHANGE_LOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/synthetic_humans.md`

## Acceptance criteria

- Endpoint generates 500 operators by default.
- Multi-skill ratio is configurable.
- Skill levels are random 1..5.
- Generated data can be listed.
