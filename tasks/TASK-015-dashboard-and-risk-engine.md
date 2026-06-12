# TASK-015: Dashboard and Risk Rule Engine

## Goal

Risk Rule Engine و داشبورد مدیریتی را بساز.

## Scope

Global risk settings from UI/API:

- Delay Risk Weight
- Material Shortage Risk Weight
- Machine Failure Risk Weight
- QC/NCR Risk Weight
- Schedule Instability Weight
- Low/Medium/High thresholds

Risk outputs:

- Order Risk
- Operation Risk
- Scenario Risk

Dashboard areas:

- delivery
- delay
- production progress
- capacity
- bottleneck
- material shortage
- NCR/rework
- optimizer performance

## Explicitly no AI

Risk is rule-based in V1.

## Required documentation updates

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/risk_dashboard.md`

## Acceptance criteria

- Risk settings can be read/updated.
- Risk scores can be calculated.
- Dashboard endpoints return aggregated data.
