# SIMULATION_ENGINE_SPEC.md

## Simulation model

Hybrid engine:

```text
Core production changes are event-based.
UI refresh/monitoring can be tick-based.
```

Internal time unit: minutes.

Simulation controls:

```text
Start
Pause
Resume
Stop
Fast-forward
Set speed factor
Create snapshot
Fork scenario
```

## Operation start conditions

An operation may start only if all are true:

```text
- Predecessor operations are finished
- Required machine is available and capable
- Required operator is available and authorized
- Required material is available/consumable
- Calendar/shift allows work
- QC/approval/release requirement is satisfied
- No blocking NCR exists for related part/operation
- Machine is not failed/maintenance/offline
```

## Queues

Separate queues:

```text
WorkCenter Queue
Machine Queue
QC Queue
Material Waiting Queue
Approval Waiting Queue
Packing Queue
Shipment Queue
```

Queue priority is calculated from:

```text
Order Priority
Internal Production Due Date
Critical Path / Slack
NCR/Rework Urgency
Material Availability
Setup Similarity
Optimizer Score
```

## Materials

On order creation:

```text
Reserve material when available.
If unavailable, create shortage and purchase/replenishment request.
```

On operation start:

```text
Consume required material.
```

Inventory values:

```text
OnHand
Reserved
Available = OnHand - Reserved
```

## Machine downtime

Support:

```text
Manual downtime
Planned maintenance
Probabilistic/random failure
```

## QC/NCR

QC is a real process step.

V1 QC result is deterministic/manual, not random.

QC fail can lead to:

```text
- repeat same operation
- rework route
- scrap
- replacement order
- NCR
```

NCR blocks only dependent operations for related part/operation, not the whole product by default.

## Outsourcing

V1 outsourcing is simple:

```text
Operation sent outside
Internal resources released
Following operations blocked until return
Lead time fixed
Events: OutsourceSent, OutsourceReturned
```
