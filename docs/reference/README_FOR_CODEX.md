# README_FOR_CODEX.md

## Purpose

This repository is for a **Full Digital Twin Prototype for factory production simulation**.

The goal is not to continue or modify the current factory planning system. The current factory system is only a **seed/source** for selected master data.

The prototype must run locally and simulate production until the user pauses/stops it.

## Canonical rule

Always distinguish these two paths:

```text
A) Understanding the current factory planning system
B) Building a new independent simulator / digital twin
```

This project is path **B**.

Use the current factory data only to seed:

```text
- BOM
- BOMParts
- Orders
- OrderParts
- Routing / Routine
- RoutingOperations / RoutineOperations
- Process / ProcessType
- Machines
- WorkCenters / Machine capabilities, if available
```

Everything else is created inside this simulator:

```text
- Synthetic operators / technicians
- Skills
- Shifts and calendars
- Synthetic materials and inventory
- Suppliers
- QC rules
- NCR workflows
- Scenarios
- Events
- Snapshots
- Current state tables
- Optimizer audit
```

## Version 1 exclusions

Do **not** implement real AI/ML in V1.

V1 must be AI-ready architecturally, but these are out of scope:

```text
- ML training
- ML prediction
- AI recommendation
- auto-learning
- LLM-driven scheduling
```

V1 decision engine:

```text
Simulation Engine
+ Rule-based Risk Engine
+ Hybrid Optimizer: heuristic + constraint optimization
+ Human approval where configured
```

## Tech stack

```text
Backend: Python + FastAPI
ORM/Models: SQLModel
Database: Local SQL Server
Frontend: React + Vite + Tailwind
Frontend server state: React Query
Frontend client state: Zustand preferred
Gantt: use a ready React Gantt library
Execution: local dev, no Docker, no login
Import: multiple CSV files, not direct DB connection
```

## Development mode

Start with backend/domain/data model first. UI comes after the domain model, database schema, import flow, event store, current state, simulation engine, optimizer contract, synthetic data generator, and scenario model are stable.

## Important implementation rule

Do not write directly to the factory database.

V1 uses CSV imports extracted from the real factory database. The simulator writes only to local `SimulatorDB`.
