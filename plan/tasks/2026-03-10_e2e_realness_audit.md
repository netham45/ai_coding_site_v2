# Task: E2E Realness Audit

## Goal

Audit the current `tests/e2e/` surface for violations of the repository's real end-to-end standard, with emphasis on fake session backends, direct DB/API shortcuts, and placeholder-style tests that do not prove a complete real runtime narrative.

## Rationale

- Rationale: The repository doctrine explicitly rejects fake session backends, in-process shortcuts as strongest proof, and staged placeholders for features that claim real E2E coverage.
- Reason for existence: This task exists to determine whether the current E2E suite actually meets the “run real command, verify real state” standard or still contains invalid proof surfaces.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/35_F36_auditable_history_and_reproducibility.md`
- `plan/e2e_tests/00_e2e_feature_generation_strategy.md`
- `plan/e2e_tests/01_e2e_harness_and_command_foundation.md`
- `plan/e2e_tests/02_e2e_core_orchestration_and_cli_surface.md`
- `plan/e2e_tests/03_e2e_session_recovery_and_child_runtime.md`
- `plan/e2e_tests/04_e2e_quality_docs_provenance_audit.md`
- `plan/e2e_tests/05_e2e_git_rectification_and_cutover.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/contracts/persistence/compile_failure_persistence.md`
- `notes/planning/implementation/real_e2e_flow_contract_phase1_decisions.md`

## Scope

- Database: review whether E2E tests bypass the claimed runtime path via direct DB assertions or direct SQL reads.
- CLI: review whether the strongest proof stays on the real CLI subprocess path.
- Daemon: review whether tests use the real daemon boundary or bypass it via in-process/API helper shortcuts.
- YAML: review whether YAML-linked behavior is proven through real compile/runtime execution rather than helper injection.
- Prompts: review whether prompt-linked E2E claims rely on real delivery/runtime surfaces.
- Tests: produce findings only; do not fix implementation or tests in this task.
- Performance: not applicable beyond bounded review-time inspection.
- Notes: add a durable review log for the audit findings.

## Verification

- Review evidence gathering: `rg -n "session_backend|fake|daemon_bridge|app_client|create_engine\\(|_db_|request\\(|pytest\\.fail|lifecycle\", \"transition" tests/e2e tests/helpers/e2e.py tests/fixtures/e2e.py`
- Document-schema targeted suite: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q`

## Exit Criteria

- The review identifies whether the current E2E surface satisfies the repository's real-runtime standard.
- Findings cite concrete file/line references for fake backends, direct shortcut usage, or placeholder tests.
- The review is recorded in a durable development log.
