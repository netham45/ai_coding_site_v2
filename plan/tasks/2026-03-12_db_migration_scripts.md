# Task: DB Migration Scripts

## Goal

Add root shell wrappers for the existing database migration commands so local operators can run upgrade and downgrade flows from `scripts/` without retyping the full CLI command.

## Rationale

- Rationale: The repository already exposes `admin db upgrade` and `admin db downgrade`, but the new root shell wrapper family is incomplete without direct migration entrypoints alongside the reset wrapper.
- Reason for existence: This task exists to keep the root command surface coherent by exposing the existing DB migration commands through stable shell entrypoints rather than forcing users to remember or recompose the raw CLI command every time.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/44_F04_validation_review_testing_docs_rectification_schema_families.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/planning/implementation/alembic_migration_discipline_decisions.md`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`

## Scope

- Database: add shell wrappers for the existing migration control path only; no database behavior changes.
- CLI: wrap `admin db upgrade` and `admin db downgrade` with optional revision passthrough.
- Daemon: not affected in this slice.
- YAML: not affected in this slice.
- Prompts: not affected in this slice.
- Tests: extend the bounded script-surface test so the new migration wrappers and their docs references are validated.
- Performance: no meaningful impact beyond one shell exec around the existing CLI command.
- Notes: update the documented root command surface to include the new DB migration wrappers.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_scripts_surface.py tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py tests/unit/test_verification_command_docs.py -q
```

## Exit Criteria

- `scripts/upgrade-db.sh` and `scripts/downgrade-db.sh` exist
- the scripts default to `head` and `base` respectively while allowing an explicit revision override
- the root docs and canonical command catalog mention the new wrappers
- bounded verification covers the scripts and authoritative-doc changes
