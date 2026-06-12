# RISK_ENGINE_SPEC.md

## V1 risk model

Rule-based only.

Risk levels:

```text
Order Risk
Operation Risk
Scenario Risk
```

Components:

```text
Delay Risk
Machine Failure Risk
QC/NCR Risk
Material Shortage Risk
Schedule Instability Risk
```

No financial risk in V1.

## Settings

Risk settings are global, not per scenario.

They must be configurable from UI:

```text
Delay Risk Weight
Material Shortage Risk Weight
Machine Failure Risk Weight
QC/NCR Risk Weight
Schedule Instability Weight
Low/Medium/High thresholds
```

## Example rules

### Delay risk

Increase if:

```text
Internal Production Due Date is near
Many operations are unfinished
Critical operations are queued
WorkCenter queue is long
```

### Material shortage risk

Increase if:

```text
Available Qty < Required Qty
Purchase request not yet arrived
Supplier lead time exceeds material required date
```

### Machine failure risk

Increase if:

```text
Machine is Failure / MaintenanceUnplanned
Machine has planned downtime inside operation window
Scenario has random failure probability enabled
```

### QC/NCR risk

Increase if:

```text
QC failed
Open NCR blocks dependent operations
Rework/replacement exists
```

### Schedule instability risk

Increase if:

```text
Re-optimization changed many operations
Frozen-window pressure is high
Manual overrides conflict with optimizer flexibility
```
