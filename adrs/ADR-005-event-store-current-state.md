# ADR-005: Event Store + Current State Tables

## Status
Accepted

## Decision
Store all important changes as events and maintain current state tables.

## Consequences
- Replay/audit/scenario fork possible.
- UI reads remain fast.
- More write complexity because event and projection/current state both need consistency.
