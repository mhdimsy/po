# OPTIMIZER_SPEC.md

## V1 optimizer type

Hybrid optimizer:

```text
1. Heuristic initial schedule
2. Constraint optimization for hard constraints
```

No AI/ML in V1.

## Hard constraints

```text
- Operation precedence
- Machine capability
- Machine availability/calendar/status
- Operator availability/calendar/status
- Operator authorization
- Material availability
- QC/approval/NCR blocking
- Frozen window
- Running operation interruption rules
- User priority override as hard constraint
```

## Running operation handling

Configurable interruptibility:

```text
Interruptible operations can be moved/paused.
Non-interruptible operations cannot.
```

## Frozen window

User-configurable per optimizer run/scenario:

```text
0 hours
2 hours
8 hours
24 hours
custom
```

## Resource reservation

Optimizer reserves future machine/operator/material resources. Re-optimization may change future reservations.

Near operation start, only machine reservation locks. Operator/material can still be adjusted.

## Objectives

User can select preset and weights.

V1 objectives:

```text
- Minimize production delay
- Maximize on-time completion
- Minimize makespan
- Improve utilization
- Reduce WIP/queues
- Respect priority
- Reduce risk
- Reduce schedule instability
```

Financial objectives are excluded in V1.

## Optimizer triggers

```text
Manual Run Optimizer
Scheduled/periodic run
Event-triggered run after important events:
- new order
- machine failure
- material arrival
- NCR opened
- priority change
- shift/capacity change
```

## Apply mode

Both modes exist:

```text
Demo mode: auto apply allowed
Serious mode: user approval required
```

## Audit

Each optimization run stores:

```text
Scenario
Optimization goal
Risk mode
Input state reference
Suggested plan
Changed operations
Reason/score
Expected impact
Accepted/rejected
User override
Timestamp
```

## Conflict alternative generation

When manual drag/drop is invalid, optimizer generates alternatives.

Show multiple options with score and metrics:

```text
Delay Impact
Risk Impact
Program Change Count
Resource Utilization Impact
Affected Orders
```
