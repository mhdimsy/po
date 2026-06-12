# TASKS_BACKLOG.md

## How Codex should work

For each task:

1. Read `README_FOR_CODEX.md` and `CONTEXT.md`.
2. Do not add AI/ML in V1.
3. Keep code modular.
4. Add tests for validation, scheduling rules, simulation state transitions, and event writes.
5. Prefer small commits.
6. Do not implement UI before backend/domain foundations unless task explicitly says so.

---

# Phase 0 — Repository foundation

## T0001 Create project structure

Create backend and frontend folders:

```text
backend/
frontend/
docs/
sample_data/
```

Backend stack:

```text
FastAPI
SQLModel
pyodbc or SQL Server-compatible driver
pytest
ruff
```

Frontend stack:

```text
React + Vite + TypeScript
Tailwind
React Query
Zustand
```

Acceptance:

```text
- backend starts with /health
- frontend starts with placeholder home
- README has local run commands
```

## T0002 Add configuration system

Backend config must support:

```text
DATABASE_URL
APP_ENV
SIMULATION_DEFAULT_SPEED
```

Acceptance:

```text
- .env.example exists
- app fails clearly if required DB config missing
```

---

# Phase 1 — Database and domain models

## T0101 Implement core import models

Implement SQLModel tables:

```text
ImportBatch
ImportFile
ImportValidationIssue
```

Acceptance:

```text
- migration/create_tables works
- CRUD smoke test passes
```

## T0102 Implement master data models

Implement:

```text
Product
BOM
BOMPart
Process
ProcessType
WorkCenter
Machine
MachineCapability
Routing
RoutingOperation
ProductionOrder
OrderPart
```

Acceptance:

```text
- relationships compile
- basic insert/query tests pass
```

## T0103 Implement generated-data models

Implement:

```text
Operator
Skill
OperatorSkill
OperatorAuthorization
Shift
CalendarEntry
MaterialItem
Warehouse
InventoryBalance
Supplier
BomItemSupplier
PurchaseRequest
```

Acceptance:

```text
- seed tests pass
```

## T0104 Implement simulation/event/scenario models

Implement:

```text
Scenario
SimulationRun
EventStore
Snapshot
ResourceReservation
OptimizationRun
ScheduleOperation
RiskRuleSetting
RiskScore
QcCheck
Ncr
NcrApproval
```

Acceptance:

```text
- can create scenario and event
- can query events by scenario/time
```

---

# Phase 2 — CSV import

## T0201 Build CSV file registry

Define expected files, columns, required fields, and FK dependencies.

Acceptance:

```text
- registry is unit-tested
- missing file/column detected
```

## T0202 Implement Validate Only endpoint

Endpoint:

```text
POST /imports/validate
```

Inputs: uploaded CSV files or local file references in dev mode.

Acceptance:

```text
- returns errors and warnings
- warnings block import
- no DB data imported during validate
```

## T0203 Implement import execution

Endpoint:

```text
POST /imports/run
```

Acceptance:

```text
- creates ImportBatch
- imports validated CSV rows
- rejects if validation has errors/warnings
- returns created entity counts
```

## T0204 Add sample CSV files

Create minimal sample data:

```text
1 product/BOM tree
3 orders
5 machines
3 work centers
10 routing operations
```

Acceptance:

```text
- sample import validates cleanly
- sample import runs successfully
```

---

# Phase 3 — Synthetic data

## T0301 Generate synthetic operators

Endpoint:

```text
POST /synthetic/operators/generate
```

Inputs:

```text
total_count
multi_skill_ratio
workcenter_shift_distribution
```

Acceptance:

```text
- creates 500 operators by default
- skill levels random 1..5
- multi-skill ratio respected approximately
- operator authorizations generated
```

## T0302 Generate synthetic inventory

Endpoint:

```text
POST /synthetic/inventory/generate
```

Presets:

```text
Plenty
Normal
Shortage-heavy
Random Chaos
```

Acceptance:

```text
- creates MaterialItem for BOM items
- creates Warehouse and InventoryBalance
- preset affects shortage level
```

## T0303 Generate synthetic suppliers

Endpoint:

```text
POST /synthetic/suppliers/generate
```

Acceptance:

```text
- creates suppliers by preset
- maps multiple suppliers to BOM items
- one default supplier per item
```

---

# Phase 4 — Event store and current state

## T0401 Implement event append service

Acceptance:

```text
- append_event writes EventStore row
- payload JSON validated
- event time uses simulation time
```

## T0402 Implement current state update services

Implement services for:

```text
order state
operation state
machine state
operator state
inventory state
queue state
```

Acceptance:

```text
- state transitions write event + update current table/entity
```

## T0403 Implement snapshots

Endpoint:

```text
POST /snapshots
```

Acceptance:

```text
- creates snapshot for scenario
- can list snapshots
```

---

# Phase 5 — Simulation engine

## T0501 Create simulation run lifecycle

Endpoints:

```text
POST /simulations/{scenario_id}/start
POST /simulations/{run_id}/pause
POST /simulations/{run_id}/resume
POST /simulations/{run_id}/stop
```

Acceptance:

```text
- simulation status changes correctly
- events written
```

## T0502 Build operation readiness evaluator

Function evaluates whether operation can start.

Acceptance:

```text
- checks predecessor, machine, operator, material, calendar, QC/NCR blocks
- returns reasons if not ready
```

## T0503 Build queue manager

Queues:

```text
WorkCenter
Machine
QC
Material
Approval
Packing
Shipment
```

Acceptance:

```text
- operations enter correct waiting queue
- priority score calculated
```

## T0504 Implement operation start/finish flow

Acceptance:

```text
- reserves/consumes material
- assigns machine/operator
- changes statuses
- writes OperationStarted/OperationFinished events
```

## T0505 Implement machine downtime

Support manual, planned, random failure.

Acceptance:

```text
- failed machine blocks operations
- repair restores availability
- events written
```

---

# Phase 6 — Materials and purchasing

## T0601 Implement shortage detection

Acceptance:

```text
- order creation attempts reservation
- shortage creates PurchaseRequest
```

## T0602 Implement supplier selection and material arrival

Acceptance:

```text
- user can select supplier
- suggested qty = shortage + safety stock percent
- material arrival updates inventory and events
```

---

# Phase 7 — QC/NCR

## T0701 Implement QC checks

Acceptance:

```text
- operations can require QC
- user can mark pass/fail
- QC status blocks dependent operations
```

## T0702 Implement NCR workflow

Acceptance:

```text
- create NCR from QC fail
- status workflow implemented
- blocks dependent operations only
```

## T0703 Implement rework/scrap/replacement choices

Acceptance:

```text
- user can choose disposition
- system creates rework or replacement order if selected
```

---

# Phase 8 — Risk engine

## T0801 Implement global risk settings

Endpoint:

```text
GET/PUT /risk/settings
```

Acceptance:

```text
- weights and thresholds editable
```

## T0802 Implement rule-based risk calculation

Acceptance:

```text
- calculates Order/Operation/Scenario risk
- stores RiskScore
```

---

# Phase 9 — Optimizer

## T0901 Implement heuristic scheduler

Acceptance:

```text
- creates valid initial schedule
- respects precedence, machine, operator, material, calendar
```

## T0902 Implement constraint optimizer placeholder/adapter

Implement adapter boundary for OR-Tools or equivalent.

Acceptance:

```text
- interface accepts current state and policy
- returns schedule proposal
- can be backed by simple implementation initially
```

## T0903 Implement optimizer run audit

Acceptance:

```text
- stores input summary, output schedule, score, changed operations
```

## T0904 Implement schedule accept/reject

Acceptance:

```text
- accepted schedule updates reservations/current schedule
- rejected schedule remains audit only
```

---

# Phase 10 — Frontend

## T1001 Import Wizard UI

Acceptance:

```text
- upload/select CSVs
- validate only
- show errors/warnings
- run import if clean
```

## T1002 Synthetic Data UI

Acceptance:

```text
- generate 500 operators
- configure multi-skill ratio
- configure inventory preset
- generate suppliers
```

## T1003 Simulation Control UI

Acceptance:

```text
- start/pause/resume/stop/fast-forward
- show simulation clock
```

## T1004 Live Operation Panel

Acceptance:

```text
- machines, operators, queues, operations live status
```

## T1005 Gantt UI

Acceptance:

```text
- schedule timeline
- drag/drop with validation
- conflict reasons
- optimizer alternatives
```

## T1006 Manager Dashboard

Acceptance:

```text
- delivery, delay, capacity, bottleneck, shortage, NCR, risk, optimizer KPIs
```

---

# Phase 11 — Polish and demo flow

## T1101 Full end-to-end demo script

Implement a repeatable demo:

```text
Import CSV
Generate synthetic data
Create scenario
Run optimizer
Start simulation
Trigger machine failure
Trigger shortage arrival
Trigger QC fail/NCR
Re-run optimizer
Show dashboard/Gantt changes
```

Acceptance:

```text
- demo can be run locally from clean DB
```
