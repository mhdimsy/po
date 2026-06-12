# TASK-014: QC / NCR / Approval

## Goal

QC/NCR/Approval را اضافه کن.

## Scope

- QC as real operation
- manual QC result: Pass/Fail
- Fail handling:
  - simple rework
  - rework routing
  - scrap
  - replacement order
- NCR model and status workflow
- simple approval workflow:
  - QC
  - Engineering
  - Production Manager
- approval decision is manual
- delayed approval blocks dependent operations

## Do not implement

- AI for NCR
- cost model
- complex approval rule engine

## Required documentation updates

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/DB_SCHEMA_CHANGE_LOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/qc_ncr_approval.md`

## Acceptance criteria

- QC Pass allows continuation.
- QC Fail can create NCR/rework/scrap/replacement path.
- Approval waiting can block dependent operations.
