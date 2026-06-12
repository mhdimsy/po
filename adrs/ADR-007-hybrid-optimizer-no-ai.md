# ADR-007: Hybrid Optimizer Without AI

## Status
Accepted

## Decision
Use heuristic scheduling plus constraint optimization for hard scheduling constraints.

## Consequences
- Heuristic provides fast initial schedules.
- Constraint optimizer enforces finite capacity rules.
- No LLM/AI controls scheduling in V1.
