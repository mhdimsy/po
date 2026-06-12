# TASK-011: Initial Optimizer without AI

## Goal

Optimizer اولیه بدون AI بساز.

## Scope

- heuristic schedule generation
- precedence constraints
- machine availability
- operator eligibility/availability
- material availability
- simple calendar handling
- order priority
- due date
- suggested schedule
- accept schedule

## Explicitly no AI

- no ML training
- no AI recommendations
- no prediction model

## No cost model

Cost is disabled in V1.

## Required documentation updates

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/optimizer.md`

## Acceptance criteria

- Run optimizer endpoint returns suggested schedule.
- Suggested schedule includes score and changed operation count.
- Schedule can be accepted.
