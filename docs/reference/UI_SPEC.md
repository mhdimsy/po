# UI_SPEC.md

## Pages

```text
Import Wizard
Synthetic Data Generator
Scenario Manager
Simulation Control
Live Operation Panel
Gantt/Schedule
Manager Dashboard
Risk Settings
QC/NCR Workbench
Material/Shortage Board
Machine/Operator Board
```

## Role views

Roles are only for display in V1, not security.

```text
Production Manager
Planner
Shop Supervisor
QC
Material
Maintenance
```

## Gantt/Schedule

Use a ready React Gantt library.

Must show:

```text
Machine timeline
Operator timeline
Order/operation timeline
Current plan
Optimizer suggested plan
Drag/drop manual change
Conflict validation
Alternative options
```

Manual drag/drop:

```text
Validate before apply.
Strict mode: if conflict exists, do not apply.
Show conflict reasons and optimizer alternatives.
```

Conflict reasons:

```text
Machine busy/down
Operator unavailable/not authorized
Material unavailable
Predecessor unfinished
Calendar/shift blocked
QC/Approval/NCR block
```

Alternative options display:

```text
Score
Delay Impact
Risk Impact
Program Change Count
Resource Utilization Impact
Affected Orders
```

## Manager dashboard KPIs

```text
Delivery
Delay
Production Progress
Capacity
Bottleneck
Material Shortage
NCR/Rework
Scenario Comparison
Optimizer Performance
```

No cost KPIs in V1.

## Optimizer KPIs

```text
Total Delay Days
On-Time Orders
Makespan
Risk Impact
Changed Operations Count
Frozen Window Violations
Resource Utilization
Scenario Score
Accepted/Rejected Plans
User Overrides
```
