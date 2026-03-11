# Task: Repo-Wide Test Audit

## Goal

Collect every pytest-discoverable test in the repository, run the full unit, integration, performance, and E2E surfaces, and produce a failure checklist that distinguishes failing files from passing and skipped coverage.

## Rationale

- Rationale: The user requested a repository-wide test and E2E execution pass with a concrete failure checklist, and this repository requires meaningful test/review work to be governed by a task plan.
- Reason for existence: This task exists to make the current proving surface explicit, execute it end to end, and record which tests fail under the current workspace state.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`
- `plan/features/47_F10_ai_cli_progress_and_stage_transition_commands.md`
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`
- `plan/checklists/04_test_coverage_and_release_readiness.md`
- `plan/checklists/16_e2e_real_runtime_gap_closure.md`
- `plan/e2e_tests/01_e2e_harness_and_command_foundation.md`
- `plan/e2e_tests/02_e2e_core_orchestration_and_cli_surface.md`
- `plan/e2e_tests/03_e2e_session_recovery_and_child_runtime.md`
- `plan/e2e_tests/04_e2e_quality_docs_provenance_audit.md`
- `plan/e2e_tests/05_e2e_git_rectification_and_cutover.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`

## Scope

- Database: exercised indirectly through integration and E2E test execution only; no schema or data changes are planned.
- CLI: exercised through the pytest surfaces that cover CLI contracts and operator/runtime entry points.
- Daemon: exercised through integration and E2E suites that start or call the daemon boundary.
- YAML: exercised through unit, integration, and E2E compilation/runtime tests that include YAML validation and builtins.
- Prompts: exercised through prompt-pack and runtime tests plus any E2E flows that render or persist prompt artifacts.
- Tests: collect every pytest-discoverable test, run all discovered suites, and capture failures and skips.
- Performance: run the existing performance pytest surface and report failures separately from functional tests.
- Notes: add a durable development log recording the executed commands and resulting status.

## Verification

- Inventory: `python3 -m pytest --collect-only -q`
- Full unit surface: `python3 -m pytest tests/unit -q`
- Full integration surface: `python3 -m pytest tests/integration -q`
- Full performance surface: `python3 -m pytest tests/performance -q`
- Full E2E surface: `python3 -m pytest tests/e2e -q`
- Full repo surface: `python3 -m pytest tests -q`

## Exit Criteria

- The complete pytest inventory is collected and summarized.
- All pytest-discoverable tests under `tests/` are executed.
- Failing test files and failing test cases are recorded accurately.
- The result is logged in `notes/logs/` with commands actually run and honest pass/fail status.
