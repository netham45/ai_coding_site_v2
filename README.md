# ai_coding_site_v2

Bootstrap scaffold for the spec-driven orchestration system described in `notes/`, `plan/`, and the user/operator documentation surfaces under `docs/`.

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

The user-documentation governance surface is being adopted through:

- `docs/README.md`
- `notes/specs/product/user_documentation_contract.md`
- `notes/catalogs/checklists/feature_checklist_standard.md`
- `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`

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
cd frontend && npm install
PYTHONPATH=src python3 -m pytest tests/unit
PYTHONPATH=src python3 -m aicoding.cli.main admin doctor
PYTHONPATH=src python3 -m aicoding.cli.main admin db ping
PYTHONPATH=src python3 -m aicoding.cli.main admin db upgrade
uvicorn aicoding.daemon.app:create_app --factory --reload
```

Common root-shell wrappers:

```bash
./scripts/upgrade-db.sh
./scripts/downgrade-db.sh
./scripts/rebuild.sh
./scripts/reset-db.sh --yes
./scripts/run-node-dev.sh
./scripts/run-server.sh
./scripts/test-e2e-bringup.sh
./scripts/test-unit.sh
./scripts/test-integration.sh
./scripts/test-e2e.sh
./scripts/test-all.sh
```

## Database bootstrap

The repository expects PostgreSQL. Set `AICODING_DATABASE_URL` in `.env` to a database owned by a role that can create tables in that database.

Typical local verification flow:

```bash
PYTHONPATH=src python3 -m aicoding.cli.main admin db ping
PYTHONPATH=src python3 -m aicoding.cli.main admin db heads
PYTHONPATH=src python3 -m aicoding.cli.main admin db upgrade
PYTHONPATH=src python3 -m aicoding.cli.main admin db check-schema
PYTHONPATH=src python3 -m pytest tests/unit
PYTHONPATH=src python3 -m pytest tests/integration
PYTHONPATH=src python3 -m pytest tests/integration/test_flow_contract_suite.py -q
```

To wipe the configured database from `.env` and replay the documented bootstrap path:

```bash
./scripts/reset-db.sh --yes
```

To run the existing migration commands directly through root shell wrappers:

```bash
./scripts/upgrade-db.sh
./scripts/downgrade-db.sh
```

Real E2E checkpoints are tracked separately from bounded and integration proof.

Use `notes/catalogs/checklists/verification_command_catalog.md` for the current canonical command families.
Use `notes/catalogs/checklists/e2e_execution_policy.md` for the current local, CI, gated/manual, and release-readiness execution expectations.
Use `docs/README.md` for the boundary between user/operator docs and internal `notes/` governance artifacts.

Current wrapper rule:

- `./scripts/test-e2e.sh` runs only canonical passing E2E checkpoints
- `./scripts/test-e2e-bringup.sh` runs quarantined real-runtime bring-up suites marked `e2e_bringup`

CI should provide a PostgreSQL service and inject `AICODING_DATABASE_URL` explicitly.

Migration discipline in the current setup phase:

- revision files live in `alembic/versions`
- revision identifiers follow `NNNN_slug_name`
- the repository currently expects a single Alembic head
- daemon and CLI schema checks compare the live database revision to that expected head instead of assuming compatibility silently

## Layout

- `docs`: user guides, operator guides, references, and runbooks
- `src/aicoding/cli`: Python CLI skeleton
- `src/aicoding/daemon`: FastAPI daemon skeleton and auth dependency
- `src/aicoding/db`: SQLAlchemy metadata and session factory foundation
- `src/aicoding/resources`: YAML, prompt, and docs assets
- `tests`: unit, integration, fixtures, factories, and performance scaffolding
- `alembic`: migration environment scaffold

## Documentation Boundary

- `docs/` contains user-facing and operator-facing documentation artifacts
- `notes/` contains governance, specifications, planning, traceability, and development logs
- `notes/scenarios/` is retained for historical scenario analysis and migration pointers; real user/operator docs belong under `docs/`
- `src/aicoding/resources/yaml/**/docs` contains machine-readable docs-definition assets, not the full user-documentation system
