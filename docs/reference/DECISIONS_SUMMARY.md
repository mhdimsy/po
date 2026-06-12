# DECISIONS_SUMMARY.md

## Product decisions

| Area | Decision |
|---|---|
| System type | Full Digital Twin Prototype |
| Data source | CSV export from factory DB |
| Imported data | BOM, Order, Routing, Process, Machine, WorkCenter |
| Generated data | Operators, skills, shifts, materials, suppliers, QC/NCR rules, scenarios |
| Simulation time | Adjustable, pause/resume/fast-forward |
| BOM/Routing | Editable inside simulator; imported BOM/Order special-audited |
| Order model | Order tree with parent/child and assignment status |
| Child orders | Auto-generated from BOM/Routing when new order is created |
| Operation assignment | Optimizer chooses machine/workcenter/operator |
| Optimizer goal | User-selectable preset + manual weights |
| Human resource | Individual real-like synthetic people |
| Skills | Skills with levels and machine/operation authorization |
| Machines | Capability, calendar, setup, failure, maintenance, operator constraint |
| Downtime | Manual + planned maintenance + probabilistic failure |
| Materials | Inventory, reservation, shortage, supplier, lead time, replenishment |
| Material level | BOM Item + Warehouse; no batch/lot/serial |
| Material consumption | Reserve on order creation; consume on operation start |
| Shortage handling | Order created, shortage recorded, replenishment request created |
| Supplier choice | User selects supplier at replenishment request |
| QC | QC is real operation with pass/fail, rework, scrap, NCR |
| QC result | Manual/deterministic in V1 |
| NCR | Full workflow; blocks dependent operations only |
| Approval | Simple workflow, timed status, final decision manual |
| Event log | Full event-sourced history |
| Replay | Snapshot + replay + scenario fork |
| Cost | Off in V1 |
| AI/ML | Off in V1 |
| Risk | Rule-based, UI-configurable global settings |
| UI | Dashboard + live operation panel + Gantt/schedule |
| Drag/drop | Strict validation, conflict reasons + optimizer alternatives |
| Auth | None in V1 |
| Environment | Local dev, no Docker |
| DB | Local SQL Server |
| Backend | FastAPI + SQLModel |
| Frontend | React + Vite + Tailwind |

## Optimizer decisions

V1 optimizer is hybrid:

```text
Heuristic initial schedule
+ constraint optimization for finite capacity constraints
```

No AI in V1.

Constraints:

```text
- Operation precedence
- Machine/workcenter availability
- Operator authorization and availability
- Material availability
- Calendar/shift
- QC/approval/NCR blocks
- Frozen window
- Non-interruptible operations
- User priority overrides as hard constraints
```

Objectives are configurable but financial goals are removed in V1.

Available objective dimensions:

```text
- Reduce delay
- Increase on-time completion
- Reduce makespan
- Improve machine/operator utilization
- Reduce WIP/queue
- Respect order priority
- Reduce schedule instability
- Reduce risk score
```

## Import decisions

CSV import is two-step:

```text
Validate Only
Import
```

Warnings block import. Import is allowed only when there are no errors and no warnings.

Each import creates an `ImportBatch`.

Imported BOM and Order are mostly protected. Direct edit is allowed only with special confirmation and audit. Before applying direct edits, show simple impact:

```text
Affected Orders Count
Affected Operations Count
Affected Materials Count
Affected Schedules Count
Need Re-Optimization: Yes/No
```

Re-optimization after direct BOM/Order edit is not automatic; system only recommends it.
