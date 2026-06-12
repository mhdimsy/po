# DOMAIN_MODEL.md

## Main bounded contexts

```text
Import
Master Data
BOM
Routing
Orders
Resources
Materials
Simulation
Optimizer
Events
Snapshots
Scenarios
QC/NCR
Risk
Dashboard
```

## Core entities

### Import

```text
ImportBatch
ImportFile
ImportValidationResult
ImportValidationIssue
```

### Master data

```text
Product
ProductFamily
MajorPartMapping
CriticalPartMapping
Process
ProcessType
WorkCenter
Machine
MachineCapability
```

### BOM

```text
BOM
BOMPart
```

### Routing

```text
Routing
RoutingOperation
AlternativeRoute
OperationMaterialRequirement
OperationResourceRequirement
```

### Orders

```text
ProductionOrder
OrderPart
OrderOperation
OrderPriority
OrderDateSet
```

### Resources

```text
Operator
Skill
OperatorSkill
OperatorAuthorization
Shift
Calendar
WorkCenterCalendar
MachineCalendar
OperatorCalendar
```

### Materials

```text
MaterialItem
Warehouse
InventoryBalance
MaterialReservation
MaterialConsumption
Supplier
BomItemSupplier
PurchaseRequest
MaterialArrival
```

### Simulation

```text
SimulationRun
SimulationClock
SimulationCommand
SimulationState
OperationQueue
ResourceReservation
```

### Optimizer

```text
OptimizationRun
OptimizationPolicy
OptimizationGoalWeight
SchedulePlan
ScheduleOperation
ScheduleChange
OptimizerOption
```

### Events

```text
EventStore
EventPayload
```

### Snapshots and scenarios

```text
Snapshot
Scenario
ScenarioFork
ScenarioSetting
```

### QC/NCR

```text
QcRule
QcCheck
Ncr
NcrApproval
ReworkOrder
ReplacementOrder
```

### Risk

```text
RiskRuleSetting
RiskScore
RiskComponent
```

## Important status enums

### Order status

```text
Created
Planned
MaterialShortage
Ready
InProduction
QC
Blocked
Finished
Delivered
Cancelled
```

### Operation status

```text
Queued
WaitingMaterial
WaitingMachine
WaitingOperator
WaitingQCApproval
Setup
Running
Paused
Stopped
BlockedByNCR
BlockedByMaintenance
Rework
Scrap
Finished
```

### Machine status

```text
Available
Reserved
Setup
Running
Idle
Blocked
WaitingOperator
WaitingMaterial
MaintenancePlanned
MaintenanceUnplanned
Failure
Repairing
Calibration
Offline
```

### Operator status

```text
Available
Reserved
Assigned
Working
WaitingMachine
WaitingMaterial
OnBreak
OffShift
Absent
OnLeave
Training
Blocked
Unavailable
```

### NCR status

```text
Draft
Open
UnderInvestigation
WaitingDisposition
DispositionDecided
WaitingApproval
Approved
Rejected
InRework
WaitingReplacement
UseAsIs
Scrapped
Closed
Cancelled
```
