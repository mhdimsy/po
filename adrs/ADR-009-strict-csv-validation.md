# ADR-009: Strict CSV Validation

## Status
Accepted

## Decision
Use two-step import: validate only, then import. Errors and warnings both block import.

## Consequences
- Dirty data cannot enter the simulator.
- Users must fix warnings before import.
- Validation layer must be explicit and helpful.
