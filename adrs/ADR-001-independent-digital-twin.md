# ADR-001: Build Independent Digital Twin, Not Extension of Query_TimeNeed

## Status
Accepted

## Context
The existing factory system has a planning snapshot built by `Query_TimeNeed` into `Query_TimeNeedTable`. That is useful for understanding current planning, but it is not a transaction/event execution model.

## Decision
Build a new independent simulator/digital twin. Use current factory data only as seed for BOM, orders, routing, processes, machines, and work centers.

## Consequences
- The simulator does not depend on `Query_TimeNeedTable` as its core.
- Simulator has its own event store and current state.
- This avoids inheriting limitations of the current backward snapshot planner.
