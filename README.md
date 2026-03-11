# ai_coding_site_v2

Bootstrap scaffold for the spec-driven orchestration system described in `notes/` and `plan/`.

## Current scope

This repository includes the setup foundation from `plan/setup/00_project_bootstrap.md` and a substantial partial implementation of the feature-plan surface under `plan/features/`.

Current repo posture:

- Python project packaging
- CLI entrypoint skeleton
- FastAPI daemon skeleton
- SQLAlchemy and Alembic foundations
- Pydantic settings and environment loading
- built-in YAML and prompt asset directories
- pytest, fixture, factory, and performance harness scaffolding
- implementation modules, migrations, and tests for many feature families described in `notes/` and `plan/features/`

The canonical feature implementation-status surface is:

- `notes/catalogs/checklists/feature_checklist_standard.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

The architectural inventory remains in:

- `notes/catalogs/inventory/major_feature_inventory.md`

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
python3 -m pytest tests/unit
python3 -m aicoding.cli.main admin doctor
python3 -m aicoding.cli.main admin db ping
python3 -m aicoding.cli.main admin db upgrade
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
python3 -m pytest tests/unit
python3 -m pytest tests/integration
python3 -m pytest tests/integration/test_flow_contract_suite.py -q
```

Real E2E checkpoints are tracked separately from bounded and integration proof.

Use `notes/catalogs/checklists/verification_command_catalog.md` for the current canonical command families.
Use `notes/catalogs/checklists/e2e_execution_policy.md` for the current local, CI, gated/manual, and release-readiness execution expectations.

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
