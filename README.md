# ai_coding_site_v2

Bootstrap scaffold for the spec-driven orchestration system described in `notes/` and `plan/`.

## Current scope

This repository currently implements the setup contract from `plan/setup/00_project_bootstrap.md`:

- Python project packaging
- CLI entrypoint skeleton
- FastAPI daemon skeleton
- SQLAlchemy and Alembic foundations
- Pydantic settings and environment loading
- built-in YAML and prompt asset directories
- pytest, fixture, factory, and performance harness scaffolding

## Environment

Copy `.env.example` to `.env` and adjust values as needed.

Local default posture:

- PostgreSQL runs locally or in CI as an external service
- the app reads connection and auth settings from environment variables
- tests run in empty-skeleton mode without requiring a live database

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
python -m aicoding.cli.main doctor
python -m aicoding.cli.main db ping
python -m aicoding.cli.main db upgrade
uvicorn aicoding.daemon.app:create_app --factory --reload
```

## Database bootstrap

The repository expects PostgreSQL. Set `AICODING_DATABASE_URL` in `.env` to a database owned by a role that can create tables in that database.

Typical local verification flow:

```bash
python3 -m aicoding.cli.main admin db ping
python3 -m aicoding.cli.main admin db heads
python3 -m aicoding.cli.main admin db upgrade
python3 -m aicoding.cli.main admin db check-schema
python3 -m pytest
```

CI should provide a PostgreSQL service and inject `AICODING_DATABASE_URL` explicitly.

Migration discipline in the current setup phase:

- revision files live in `alembic/versions`
- revision identifiers follow `NNNN_slug_name`
- the repository currently expects a single Alembic head
- daemon and CLI schema checks compare the live database revision to that expected head instead of assuming compatibility silently

## Layout

- `src/aicoding/cli`: Python CLI skeleton
- `src/aicoding/daemon`: FastAPI daemon skeleton and auth dependency
- `src/aicoding/db`: SQLAlchemy metadata and session factory foundation
- `src/aicoding/resources`: YAML, prompt, and docs assets
- `tests`: unit, integration, fixtures, factories, and performance scaffolding
- `alembic`: migration environment scaffold
