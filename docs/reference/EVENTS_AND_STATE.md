# EVENTS_AND_STATE.md

## Event store principle

Every important state change must be written as an event.

Current state tables are updated from commands/events for fast reads. Event store is the source for audit/replay/history.

## Event naming convention

Use past-tense domain events:

```text
OrderCreated
OrderTreeGenerated
MaterialReserved
ShortageDetected
PurchaseRequestCreated
SupplierSelected
MaterialArrived
OperationQueued
OperationScheduled
MachineReserved
OperatorReserved
OperationStarted
OperationPaused
OperationResumed
OperationFinished
MachineFailed
MachineRepairStarted
MachineRepairFinished
MaintenanceStarted
MaintenanceFinished
QCStarted
QCPassed
QCFailed
NCROpened
NCRDispositionDecided
NCRApprovalRequested
NCRApproved
NCRRejected
ReworkCreated
ReplacementOrderCreated
OutsourceSent
OutsourceReturned
OptimizerRunStarted
ScheduleSuggested
ScheduleAccepted
ScheduleRejected
SnapshotCreated
ScenarioForked
PackingStarted
PackingFinished
ShipmentStarted
Delivered
```

## Current state projections

Maintain tables/projections for:

```text
CurrentOrderState
CurrentOperationState
CurrentMachineState
CurrentOperatorState
CurrentInventoryState
CurrentSchedule
CurrentQueueState
CurrentRiskState
CurrentScenarioState
```

## Snapshot policy

Snapshots are created:

```text
- Manually by user
- Periodically by simulation settings
- Before optimizer run
- Before scenario fork
```

## Replay use cases

```text
- Audit why a plan changed
- Replay from snapshot to a point in time
- Fork scenario from old state
- Compare scenarios from same base state
- Build future training data
```

## Minimal event payload pattern

```json
{
  "event_type": "OperationStarted",
  "scenario_id": 1,
  "simulation_run_id": 5,
  "aggregate_type": "OrderOperation",
  "aggregate_id": 12345,
  "event_time": "2026-06-12T08:30:00",
  "payload": {
    "order_id": 100,
    "operation_id": 12345,
    "machine_id": 7,
    "operator_id": 55
  }
}
```
