# ShopAPI

FastAPI e-commerce backend, built step by step in a 20-day course.

## Stack

- Python 3.12+, FastAPI, Pydantic v2
- SQLAlchemy 2.0 async with asyncpg; Alembic for migrations
- PostgreSQL (plus Redis and Adminer) in Docker Compose; the app itself runs locally
- Learners use Windows and PowerShell: give PowerShell commands, use `curl.exe` not `curl`

## Layout

- `app/main.py`: creates the app, includes routers, registers the error handler
- `app/core/`: shared pieces (config, database, exceptions, errors)
- `app/modules/<module>/`: `models.py`, `schemas.py`, `service.py`, `router.py`
- `migrations/`: Alembic (`migrations/versions/` holds revisions)

## Rules

- Routers speak HTTP only: read the request, call one service function, return its result. No queries, no business rules, no try/except.
- Services hold the business rules. They never import FastAPI, never raise HTTPException, never use status codes.
- Services raise domain exceptions: `NotFoundError`, `ConflictError`, `BusinessRuleError` from `app/core/exceptions.py`, or module subclasses of them.
- One handler in `app/core/errors.py` maps them to 404 / 409 / 400.
- Public service functions return Pydantic Read schemas, never SQLAlchemy models. Private helpers start with an underscore.
- Other modules use a module only through its `service.py`.
- Pydantic v2 and SQLAlchemy 2.0 style only (`model_dump`, `model_config`, `Mapped`/`mapped_column`, `select()`; no `orm_mode`, `.dict()`, `session.query`).
- Every schema change is an Alembic migration. Always name constraints explicitly.
- Never run `alembic upgrade` / `alembic downgrade`, `git commit`, or anything that deletes data unless asked. Show the command instead.

## Commands

- Start services: `docker compose up -d`, then `docker compose ps` until healthy
- Run the app: `fastapi dev app/main.py` (http://127.0.0.1:8000/docs)
- Create a migration: `alembic revision --autogenerate -m "describe the change"`, then review the generated file in `migrations/versions/`
- Apply migrations (user runs it): `alembic upgrade head`
- Check current revision: `alembic current`
