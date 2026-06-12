# CODEX_REVIEW_CHECKLIST.md

Use this checklist after each Codex change.

## Must not violate

```text
[ ] No AI/ML implemented in V1
[ ] No Docker added
[ ] No login/auth added
[ ] No direct production DB connection
[ ] No message broker
[ ] No material cost model
[ ] No financial optimizer goal
```

## Backend

```text
[ ] FastAPI app starts
[ ] SQLModel models are typed
[ ] SQL Server config is externalized
[ ] Module boundaries respected
[ ] Errors are clear
[ ] Tests added for new logic
```

## Import

```text
[ ] Validate-only does not write domain data
[ ] Warnings block import
[ ] FK validations are explicit
[ ] ImportBatch created only on import
```

## Events/state

```text
[ ] Important state changes append events
[ ] Current state updated consistently
[ ] ScenarioId is included where needed
```

## Simulation

```text
[ ] Operation cannot start unless readiness rules pass
[ ] Blocking reason is explainable
[ ] Time unit is minutes internally
```

## Optimizer

```text
[ ] Respects hard constraints
[ ] Does not use AI
[ ] Stores audit for runs
```
