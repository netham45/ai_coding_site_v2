# Task: E2E Baseline And Operator CLI Surface

## Goal

Review the existing E2E plans, establish a real-runtime baseline by running the currently available non-gated E2E suite, log any observed failures without fixing product code, and add one new operator-surface E2E test aligned to the phase-02 E2E plan.

## Rationale

- Rationale: The repository already contains a substantial real E2E surface, but the phase plans under `plan/e2e_tests/` still need concrete incremental execution and additional suite-family implementation to move from planning to actual runtime proof.
- Reason for existence: This task exists to convert the E2E plans into current runnable proof, make current breakage visible in a durable failure log, and begin filling the planned operator-surface suite family without silently fixing unrelated product defects.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/e2e_tests/00_e2e_feature_generation_strategy.md`
- `plan/e2e_tests/01_e2e_harness_and_command_foundation.md`
- `plan/e2e_tests/02_e2e_core_orchestration_and_cli_surface.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`
- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/48_F11_operator_structure_and_state_commands.md`
- `plan/features/49_F11_operator_history_and_artifact_commands.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/e2e_tests/README.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `notes/planning/implementation/real_e2e_flow_contract_phase1_decisions.md`

## Scope

- Database: use the real PostgreSQL-backed E2E harness and verify durable operator-visible state and event history through real runtime execution.
- CLI: add and run a real CLI subprocess E2E test for the operator inspection/pause surface.
- Daemon: run the real daemon subprocess for baseline and targeted E2E coverage.
- YAML: exercise builtin YAML/runtime behavior only through the existing real workflow path needed by the new operator-surface test.
- Prompts: exercise prompt-backed workflow start only as required to create the real runtime state used by the operator-surface test.
- Tests: run the current non-gated real-E2E baseline, add one operator-surface E2E test file, and rerun targeted commands.
- Performance: accept the current multi-minute runtime for gated E2E baseline execution and keep the new targeted suite bounded.
- Notes: add a durable failure log for current observed E2E breakage and update canonical command docs for the new runnable E2E surface.

## Verification

- Document-schema targeted suite: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_verification_command_docs.py tests/unit/test_e2e_execution_policy_docs.py tests/unit/test_task_plan_docs.py -q`
- Existing non-gated E2E baseline: `python3 -m pytest tests/e2e -q -m 'e2e_real and not requires_tmux and not requires_git and not requires_ai_provider'`
- New operator-surface E2E test: `python3 -m pytest tests/e2e/test_e2e_operator_cli_surface.py -q`

## Exit Criteria

- The current non-gated E2E baseline has been run and its result is captured honestly.
- Observed baseline failures are recorded in a new durable log file without product-code fixes.
- A new operator-surface E2E suite file exists under `tests/e2e/` and runs through the real daemon plus real CLI path.
- Canonical command docs mention the new targeted E2E command.
- Updated authoritative docs and task artifacts pass the relevant document-schema tests.
