# Task: E2E Prompt And Summary History Surface

## Goal

Add and run a real E2E suite for prompt-history and summary-history behavior using the real daemon, real CLI subprocess path, and real PostgreSQL-backed runtime harness.

## Rationale

- Rationale: The E2E feature matrix already assigns prompt and summary history to a dedicated real suite target, but that target does not yet exist as a runnable file in `tests/e2e/`.
- Reason for existence: This task exists to move prompt/history coverage from plan-only status to actual real-runtime proof without bundling unrelated runtime fixes into the same change.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/e2e_tests/04_e2e_quality_docs_provenance_audit.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`
- `plan/features/31_F28_prompt_history_and_summary_history.md`
- `plan/features/43_F05_prompt_pack_authoring.md`
- `plan/features/45_F04_runtime_policy_and_prompt_schema_families.md`
- `plan/features/58_F31_database_session_attempt_history_schema_family.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/specs/database/database_schema_spec_v2.md`

## Scope

- Database: verify durable prompt and summary history through the real PostgreSQL-backed runtime path.
- CLI: drive prompt, context, summary registration, prompt-history, prompt-show, summary-history, and summary-show through the real CLI subprocess path.
- Daemon: use the real daemon subprocess and real API-owned persistence behavior behind the CLI commands.
- YAML: rely on the real built-in workflow/task/subtask definitions needed to deliver prompt and summary records.
- Prompts: prove delivered prompt records and prompt history through the real runtime-selected prompt path.
- Tests: add one new real E2E suite file and run it directly.
- Performance: keep the suite bounded to one node and one subtask attempt.
- Notes: update canonical command docs and maintain a current development log for this task.

## Verification

- Prompt/history E2E suite: `python3 -m pytest tests/e2e/test_e2e_prompt_and_summary_history_real.py -q`
- Document-schema targeted suite: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_verification_command_docs.py tests/unit/test_e2e_execution_policy_docs.py tests/unit/test_task_plan_docs.py -q`

## Exit Criteria

- `tests/e2e/test_e2e_prompt_and_summary_history_real.py` exists and runs through the real daemon plus real CLI path.
- The suite proves prompt delivery history, prompt-record inspection, summary registration history, and summary-record inspection through real durable state.
- Canonical command docs mention the new targeted E2E command.
- Required task and development-log artifacts are current and pass the relevant document-schema tests.
