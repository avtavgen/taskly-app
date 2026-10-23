---
name: backend-tests
description: Write and run pytest unit tests for the FastAPI backend.
---

- Tests live in `backend/tests/`, mirroring `backend/app/` (e.g. `app/routers/tasks.py` → `tests/test_tasks.py`). Check existing tests and fixtures (`conftest.py`) first and reuse them.
- Use `pytest`, FastAPI `TestClient`, and `dependency_overrides` / mocks for DB and external calls. Cover: happy path, validation errors (422), not-found (404), edge cases.
- Run from `backend/`:
```
  cd backend && python -m pytest --cov=app --cov-report=term-missing
```
- Report coverage for the changed files from the `term-missing` output.