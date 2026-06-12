# ARCHITECTURE.md

## Architecture style

Start as a **modular monolith** with clear module boundaries. Do not create physical microservices in V1.

The code should be structured so that these modules can later be split into services:

```text
app/
  main.py
  core/
    config.py
    db.py
    time.py
    errors.py
  modules/
    import_factory/
    master_data/
    bom/
    routing/
    orders/
    resources/
    materials/
    simulation/
    optimizer/
    events/
    snapshots/
    scenarios/
    qc_ncr/
    risk/
    dashboard/
    gantt/
```

## Logical services inside modular monolith

```text
API Service
Simulation Engine
Optimizer Service
Event Processor
Risk Engine
Import Service
Synthetic Data Generator
Dashboard Query Layer
```

## Communication

In V1, use direct Python module calls inside the backend and REST endpoints for UI access. Do not use RabbitMQ/Kafka.

## Database

Local SQL Server.

Use SQLModel for ORM and Pydantic-compatible schemas.

Use current state tables plus event store.

## Backend command/API flow examples

```text
POST /imports/validate
POST /imports/run
POST /synthetic/operators/generate
POST /synthetic/inventory/generate
POST /scenarios
POST /simulations/{scenario_id}/start
POST /simulations/{scenario_id}/pause
POST /simulations/{scenario_id}/resume
POST /simulations/{scenario_id}/fast-forward
POST /optimizer/run
POST /schedules/{schedule_id}/accept
POST /schedules/{schedule_id}/reject
GET  /dashboard/manager
GET  /dashboard/live
GET  /gantt/schedule
```

## Frontend structure

```text
src/
  api/
  app/
  components/
  pages/
    ImportWizard/
    SyntheticData/
    SimulationControl/
    LiveOperations/
    GanttSchedule/
    ManagerDashboard/
    ScenarioManager/
    RiskSettings/
    QcNcr/
  stores/
  hooks/
  types/
```

## State management

Use React Query for server state.

Use Zustand for UI/client state:

```text
selectedScenario
selectedSimulationTime
simulationControls
ganttZoomAndFilters
dragDropDraft
optimizerComparisonView
selectedMachineOrderOperator
```
