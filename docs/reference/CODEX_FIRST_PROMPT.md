# CODEX_FIRST_PROMPT.md

Use this prompt as the first instruction to Codex after placing all docs in the repo.

```text
You are working on a local Full Digital Twin Prototype for factory production simulation.

Before coding, read these files in order:

1. docs/README_FOR_CODEX.md
2. docs/CONTEXT.md
3. docs/DECISIONS_SUMMARY.md
4. docs/ARCHITECTURE.md
5. docs/TASKS_BACKLOG.md
6. docs/ADR_INDEX.md

Important constraints:

- V1 has no AI/ML.
- V1 runs locally without Docker.
- Backend is Python FastAPI + SQLModel.
- Database is local SQL Server.
- Frontend is React + Vite + Tailwind.
- Start backend/domain/data model first.
- Use modular monolith structure.
- Use CSV import, not direct factory DB connection.
- Maintain Event Store + Current State tables.
- Implement tasks incrementally from TASKS_BACKLOG.md.

Start with Phase 0 and Phase 1 only.
Do not implement frontend yet except creating the frontend scaffold.
Do not implement AI/ML.
Do not implement Docker.

After reading docs, produce a short implementation plan, then create the project skeleton and initial health endpoint.
```
