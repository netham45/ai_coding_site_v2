# Task: Root Scripts Command Surface

## Goal

Add repository-root shell entrypoints under `scripts/` for the common local workflows the repo currently documents separately: frontend rebuild, frontend Vite dev, daemon runtime, and unit/integration/E2E/all test execution.

## Rationale

- Rationale: The current command surface is split across `README.md`, `frontend/README.md`, and the verification catalog, which makes routine local startup and verification more tedious than necessary.
- Reason for existence: This task exists to add one consistent root-level shell entrypoint family without inventing new behavior or drifting from the canonical commands already documented in the repo.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`
- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/34_F32_automation_of_all_user_visible_actions.md`
- `plan/features/44_F04_validation_review_testing_docs_rectification_schema_families.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `frontend/README.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`

## Scope

- Database: not directly changed; the scripts only wrap existing startup and verification commands that may talk to PostgreSQL when those commands already do.
- CLI: expose the current CLI/pytest command families through stable root shell wrappers instead of requiring manual directory changes.
- Daemon: expose the existing Uvicorn daemon startup command through a root shell wrapper.
- YAML: not affected in this slice.
- Prompts: not affected in this slice.
- Tests: add bounded proof that the new shell scripts exist at the expected paths and continue to wrap the documented canonical commands.
- Performance: keep the wrappers minimal so they add no meaningful overhead beyond a directory change and process exec.
- Notes: update the repo quickstart and verification docs so the new shell entrypoints are discoverable and their intent is explicit.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_scripts_surface.py tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py tests/unit/test_verification_command_docs.py -q
```

## Exit Criteria

- `scripts/rebuild.sh`, `scripts/run-node-dev.sh`, `scripts/run-server.sh`, `scripts/test-unit.sh`, `scripts/test-integration.sh`, `scripts/test-e2e.sh`, and `scripts/test-all.sh` exist
- each script runs from any current working directory by resolving the repo root from its own path
- the script behavior matches the commands already documented in the repo rather than inventing a parallel workflow
- the README and verification catalog point readers at the new wrappers while preserving the underlying canonical commands
- the development log records the work, commands run, and the resulting status honestly
