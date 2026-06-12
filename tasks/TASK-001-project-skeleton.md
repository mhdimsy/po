# TASK-001: Project Skeleton

## Goal

اسکلت اولیه repo را بساز.

## Scope

- Backend با FastAPI
- Frontend با React + Vite + Tailwind
- ساختار modular monolith
- بدون Docker
- بدون Login
- بدون domain logic
- health check ساده backend
- صفحه ساده frontend

## Do not implement

- SQL Server connection
- database models
- import
- simulation
- optimizer
- auth
- Docker

## Expected structure

```text
backend/
  app/
    main.py
    core/
    modules/
    shared/
  pyproject.toml or requirements.txt
frontend/
  src/
  package.json
  vite.config.*
docs/
logs/
tasks/
```

## Required documentation updates

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/TESTING_LOG.md`
- `docs/PROJECT_STATUS.md`
- Create `docs/modules/project_structure.md`

## Acceptance criteria

- Backend runs locally.
- `GET /health` returns OK.
- Frontend runs locally.
- README contains local run commands.
