# Task: Reset DB Script

## Goal

Add a guarded root shell script that fully wipes the PostgreSQL database configured in `.env`/`AICODING_DATABASE_URL` and then rebuilds it using the repository's documented bootstrap commands.

## Rationale

- Rationale: The repo already documents how to bootstrap the database, but it does not provide a single repeatable local command for clearing the configured database and replaying that bootstrap path.
- Reason for existence: This task exists to make destructive local database reset explicit, reproducible, and aligned with the current documented command family instead of relying on ad hoc SQL or partial Alembic sequences.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/44_F04_validation_review_testing_docs_rectification_schema_families.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/planning/implementation/setup_bootstrap_decisions.md`
- `notes/logs/features/2026-03-11_yaml_schema_and_field_rigidity_implementation.md`

## Scope

- Database: add a local destructive reset wrapper that clears owned objects in the configured PostgreSQL database and then reapplies the documented migration/bootstrap commands.
- CLI: reuse the existing `admin db ping`, `admin db heads`, `admin db upgrade`, and `admin db check-schema` surfaces exactly as documented.
- Daemon: not directly affected in this slice.
- YAML: not affected in this slice.
- Prompts: not affected in this slice.
- Tests: extend bounded script-surface coverage so the new reset wrapper and its docs references are validated.
- Performance: keep the script on the existing DB bootstrap path without extra catalog scans beyond the helper reset and current CLI checks.
- Notes: document the new reset wrapper in the root quickstart/DB bootstrap surface and in the canonical verification catalog.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_scripts_surface.py tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py tests/unit/test_verification_command_docs.py -q
```

## Exit Criteria

- `scripts/reset-db.sh` exists and refuses to run destructively without explicit confirmation
- the script wipes the configured database through the repo's `reset_public_schema()` helper rather than recreating `public`
- the script replays the documented bootstrap commands after the wipe
- README and canonical command docs mention the new reset wrapper
- bounded verification covers the new script and the authoritative-doc updates
