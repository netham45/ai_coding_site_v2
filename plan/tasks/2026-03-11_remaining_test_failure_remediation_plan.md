# Task: Remaining Test Failure Remediation

## Goal

Investigate, justify, implement, and verify the fixes for every test that still fails after the repository-wide `pytest -n auto --dist=loadfile` parallel run is made infrastructure-safe.

## Rationale

- Rationale: The full-worker parallel surface is now stable enough to expose the real remaining defects instead of fixture contention, but the repo still has `16` failing tests across unit, integration, performance, and real E2E layers.
- Reason for existence: This task exists to convert the current failure list into an ordered remediation program with shared-root-cause grouping, explicit proof targets, and an implementation sequence that prevents churn between low-level contracts and higher-level E2E assertions.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/35_F36_auditable_history_and_reproducibility.md`
- `plan/features/41_F03_variable_substitution_and_context_rendering.md`
- `plan/features/43_F05_prompt_pack_authoring.md`
- `plan/features/54_F03_hook_expansion_and_policy_resolution_compile_stage.md`
- `plan/features/57_F31_database_runtime_state_schema_family.md`
- `plan/features/69_F21_F22_F23_F29_turnkey_quality_gate_finalize_chain.md`
- `plan/tasks/2026-03-11_repo_wide_test_audit.md`
- `plan/tasks/2026-03-11_parallel_all_tests_meta_verifier_plan.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/planning/implementation/pytest_fixture_architecture_decisions.md`
- `notes/planning/implementation/resource_and_test_scaffolding_decisions.md`
- `notes/logs/reviews/2026-03-11_repo_wide_test_audit.md`

## Scope

- Database: fix migration-status and runtime-state view behavior so bounded and daemon-facing tests agree on revision state, dependency blocker rows, and materialization status payloads.
- CLI: fix CLI-facing workflow, compile-failure, and audit round-trip behavior where the current command outputs no longer match the tested contracts.
- Daemon: fix reproducibility snapshots, audit endpoints, child materialization/reporting, and any timeout or source-discovery behavior that now fails in real E2E or daemon integration tests.
- YAML: confirm whether builtin/project YAML contracts changed intentionally or whether hook-selection, compile-failure, and source-discovery outputs drifted from the documented/tested behavior.
- Prompts: fix render-context coverage or prompt templates where canonical variables such as `subtask.key` are now required but not supplied by the tested render contexts.
- Tests: remediate all remaining failing unit, integration, performance, and E2E tests; update tests only when the tested contract is obsolete and the newer contract is documented/justified.
- Performance: distinguish true product regressions from benchmark-budget drift after logic fixes, then either optimize the product path or update thresholds with explicit justification.
- Notes: update authoritative notes and logs whenever investigation shows an intentional contract change, new invariant, or corrected verification command.

## Current State

After the latest full-worker command:

```bash
python3 -m pytest tests -n auto --dist=loadfile -q --ignore tests/integration/test_parallel_all_tests_meta.py -m "not requires_ai_provider"
```

the suite finishes with:

- `16 failed, 729 passed`

The current failing tests are:

1. `tests/performance/test_harness.py::test_default_prompt_pack_load_and_render_complete_quickly`
2. `tests/performance/test_harness.py::test_runtime_state_view_queries_complete_quickly`
3. `tests/integration/test_database_lifecycle.py::test_runtime_state_views_reflect_live_state`
4. `tests/integration/test_daemon.py::test_db_schema_compatibility_reports_revision_state`
5. `tests/performance/test_harness.py::test_turnkey_quality_chain_completes_quickly`
6. `tests/performance/test_harness.py::test_workflow_compile_with_hook_expansion_completes_quickly`
7. `tests/unit/test_reproducibility.py::test_load_run_audit_snapshot_by_node_includes_attempts_and_prompt_summary_history`
8. `tests/e2e/test_flow_19_hook_expansion_compile_stage_real.py::test_flow_19_hook_expansion_compile_stage_runs_against_real_daemon_and_real_cli`
9. `tests/e2e/test_flow_03_materialize_and_schedule_children_real.py::test_flow_03_materialize_and_schedule_children_runs_against_real_daemon_and_real_cli`
10. `tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py::test_flow_20_compile_failure_and_reattempt_runs_against_real_daemon_and_real_cli`
11. `tests/unit/test_workflows.py::test_compile_task_workflow_renders_canonical_variables_and_invoker_context`
12. `tests/integration/test_daemon.py::test_node_and_run_audit_endpoints_return_reconstructible_history`
13. `tests/e2e/test_e2e_full_epic_tree_runtime_real.py::test_e2e_full_epic_tree_git_merge_propagates_task_changes_to_plan_phase_and_epic`
14. `tests/integration/test_daemon.py::test_child_materialization_endpoints_materialize_and_report_scheduling`
15. `tests/integration/test_session_cli_and_daemon.py::test_cli_node_and_run_audit_round_trip`
16. `tests/performance/test_harness.py::test_provenance_refresh_and_lookup_complete_quickly`

## Investigation Findings

### 1. Rendering-contract drift is affecting both unit and performance layers

Evidence:

- `tests/unit/test_workflows.py` reports canonical render-variable ordering/contents drift.
- `tests/performance/test_harness.py::test_default_prompt_pack_load_and_render_complete_quickly` fails with `TemplateRenderError` for missing `subtask.key`.
- `src/aicoding/rendering.py` still flattens only the scopes supplied by the caller and does not synthesize missing task/subtask aliases.

Implication:

- either prompt assets now legitimately require `subtask.*` variables and the render-context builders/tests are stale
- or prompt assets/regression code introduced a variable that the documented render contract never promised

This bucket should be fixed before revisiting compile and hook-expansion timings because compile performance depends on stable rendering.

### 2. Reproducibility snapshot models drifted from durable attempt schema

Evidence:

- `tests/unit/test_reproducibility.py`, `tests/integration/test_daemon.py::test_node_and_run_audit_endpoints_return_reconstructible_history`, and `tests/integration/test_session_cli_and_daemon.py::test_cli_node_and_run_audit_round_trip` all fail with `SubtaskAttemptSnapshot.__init__()` missing `execution_result_json`.
- `src/aicoding/daemon/reproducibility.py::_attempt_snapshot()` does not populate that field even though the snapshot type now requires it.

Implication:

- the durable model and reproducibility snapshot schema are out of sync
- fixing the low-level snapshot constructor should unlock three failing surfaces at once

### 3. Runtime-state view semantics have drifted in at least two ways

Evidence:

- `tests/integration/test_database_lifecycle.py::test_runtime_state_views_reflect_live_state` and the matching performance test both fail because `pending_dependency_nodes` returns multiple rows where the tests expect one.
- `tests/integration/test_daemon.py::test_db_schema_compatibility_reports_revision_state` reports `up_to_date` where the test expects `uninitialized`.
- `tests/integration/test_daemon.py::test_child_materialization_endpoints_materialize_and_report_scheduling` and `tests/e2e/test_flow_03_materialize_and_schedule_children_real.py` disagree with the current child scheduling/materialization payloads (`ready_child_count` and `blocked` vs `blocked_on_dependency` status).

Implication:

- either the SQL views are over-producing rows after dependency/materialization changes
- or the tests still encode the previous view contract and need coordinated contract updates plus note changes

This bucket should be fixed before the E2E child-materialization and full-tree narratives, because those higher layers depend on the same status semantics.

### 4. Hook-expansion and compile-failure command surfaces appear to have changed contract

Evidence:

- `tests/e2e/test_flow_19_hook_expansion_compile_stage_real.py` shows selected hook ordering/ids no longer matching the expected `default_hooks`-first contract.
- `tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py` now gets `404 compiled workflow not found` from `workflow source-discovery` after a failed compile.
- `tests/performance/test_harness.py::test_workflow_compile_with_hook_expansion_completes_quickly` also misses its budget, which may be partly a byproduct of the same hook/policy behavior drift.

Implication:

- the compile-stage contract may have narrowed to “source discovery only exists for successful compiles,” or the daemon stopped persisting enough failure-stage metadata
- the hook-selection output may have been intentionally normalized or accidentally reordered/grouped

This bucket needs explicit contract review before changing tests, because these are user/operator-facing compile diagnostics.

### 5. Remaining E2E/full-runtime failures appear to be downstream effects plus one daemon-availability path

Evidence:

- `tests/e2e/test_e2e_full_epic_tree_runtime_real.py::test_e2e_full_epic_tree_git_merge_propagates_task_changes_to_plan_phase_and_epic` still hits a daemon-unavailable timeout mid-flow.
- the same full-tree file previously showed lifecycle-state expectation drift (`READY` vs `RUNNING`) in focused runs.
- `tests/performance/test_harness.py::test_turnkey_quality_chain_completes_quickly` and `tests/performance/test_harness.py::test_provenance_refresh_and_lookup_complete_quickly` are likely sensitive to the same compile/runtime surfaces and should be re-measured after the contract bugs are fixed.

Implication:

- these should be addressed last, after rendering, reproducibility, runtime-state, and compile diagnostics are stable
- otherwise the E2E investigation will keep rediscovering lower-layer issues

## Design Objectives

The remediation task should satisfy all of the following:

1. Fix root causes in the lowest layer that can explain multiple failing tests at once.
2. Prefer code fixes over test edits when the failing test still reflects the documented contract.
3. When the contract has genuinely changed, update the relevant notes and all affected tests in the same change.
4. Re-run the narrowest proving surface after each fix batch before widening to broader integration or E2E suites.
5. Preserve the now-working `-n auto` parallel infrastructure while resolving logic failures.
6. End with the authoritative full-worker parallel command green, or leave an explicit logged residual failure set if blocked by external capabilities.

## Proposed Remediation Workstreams

### Workstream A: Rendering and prompt-context contract

Targets:

- `tests/unit/test_workflows.py::test_compile_task_workflow_renders_canonical_variables_and_invoker_context`
- `tests/performance/test_harness.py::test_default_prompt_pack_load_and_render_complete_quickly`

Primary investigation questions:

- which prompt files now reference `subtask.key`
- whether `build_render_context()` callers should provide `task`/`subtask` aliases in more places
- whether variable ordering in compiled payloads is contractually meaningful or an incidental assertion

Likely implementation surfaces:

- `src/aicoding/rendering.py`
- compile-stage context assembly under workflow compilation
- prompt assets under `src/aicoding/resources/prompts/packs/default/`
- the affected unit/performance tests

Why first:

- rendering drift is low-level and deterministic
- compile, hook-expansion, and prompt-pack performance all depend on it

### Workstream B: Reproducibility and audit snapshot schema alignment

Targets:

- `tests/unit/test_reproducibility.py::test_load_run_audit_snapshot_by_node_includes_attempts_and_prompt_summary_history`
- `tests/integration/test_daemon.py::test_node_and_run_audit_endpoints_return_reconstructible_history`
- `tests/integration/test_session_cli_and_daemon.py::test_cli_node_and_run_audit_round_trip`

Primary investigation questions:

- when `execution_result_json` became required in `SubtaskAttemptSnapshot`
- whether other newly required fields are also absent from snapshot serializers
- whether snapshot ordering or payload shape changed beyond the constructor mismatch

Likely implementation surfaces:

- `src/aicoding/daemon/reproducibility.py`
- snapshot model definitions under the daemon/model layer
- any CLI response normalization using those snapshots

Why second:

- one low-level serializer fix likely clears three failures
- these are bounded and integration-friendly, with no live E2E dependency

### Workstream C: Migration-status and runtime-state view semantics

Targets:

- `tests/integration/test_database_lifecycle.py::test_runtime_state_views_reflect_live_state`
- `tests/performance/test_harness.py::test_runtime_state_view_queries_complete_quickly`
- `tests/integration/test_daemon.py::test_db_schema_compatibility_reports_revision_state`
- `tests/integration/test_daemon.py::test_child_materialization_endpoints_materialize_and_report_scheduling`
- `tests/e2e/test_flow_03_materialize_and_schedule_children_real.py::test_flow_03_materialize_and_schedule_children_runs_against_real_daemon_and_real_cli`

Primary investigation questions:

- why `pending_dependency_nodes` now returns multiple rows for one blocked node
- whether `migration_status()` is correct and the daemon test setup is stale, or vice versa
- whether child scheduling should expose `blocked_on_dependency` everywhere or collapse to `blocked` in some operator surfaces
- whether `ready_child_count` should reflect only initial materialization or the post-materialization steady state

Likely implementation surfaces:

- `src/aicoding/db/migrations.py`
- SQL view definitions in Alembic migrations and related query loaders
- `src/aicoding/daemon/materialization.py`
- operator/daemon response-model translation layers

Why third:

- these semantics are shared by bounded, daemon, and E2E tests
- fixing them before compile-stage E2E avoids masking state-model problems as runtime-flow problems

### Workstream D: Compile-stage diagnostics and hook-expansion contract

Targets:

- `tests/e2e/test_flow_19_hook_expansion_compile_stage_real.py::test_flow_19_hook_expansion_compile_stage_runs_against_real_daemon_and_real_cli`
- `tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py::test_flow_20_compile_failure_and_reattempt_runs_against_real_daemon_and_real_cli`
- `tests/performance/test_harness.py::test_workflow_compile_with_hook_expansion_completes_quickly`

Primary investigation questions:

- whether hook selection is supposed to be grouped or ordered differently now
- whether failed compiles are supposed to retain source-discovery information
- whether compile-failure diagnostics should work without a persisted compiled workflow
- whether hook-expansion cost regressions are a product bug or a benchmark threshold that must be updated after intentional behavior changes

Likely implementation surfaces:

- `src/aicoding/daemon/workflows.py`
- compile-failure persistence and source-discovery loaders
- hook policy/hook listing handlers and CLI surfaces
- related notes covering compile diagnostics

Why fourth:

- these surfaces are higher-level than raw rendering/runtime-state but still bounded enough to debug before full live E2E

### Workstream E: Full-runtime and residual performance closure

Targets:

- `tests/e2e/test_e2e_full_epic_tree_runtime_real.py::test_e2e_full_epic_tree_git_merge_propagates_task_changes_to_plan_phase_and_epic`
- `tests/performance/test_harness.py::test_turnkey_quality_chain_completes_quickly`
- `tests/performance/test_harness.py::test_provenance_refresh_and_lookup_complete_quickly`

Primary investigation questions:

- whether the full-tree daemon timeout is still a runtime bug after the lower-level contract fixes
- whether the turnkey-quality and provenance budgets recover once the lower-level regressions are fixed
- if not, whether the implementation should be optimized or the budgets should be intentionally revised with note support

Likely implementation surfaces:

- live daemon/runtime orchestration around long-running flows
- provenance refresh code paths
- quality-chain orchestration
- real E2E helper timing assumptions

Why last:

- these are the most integration-heavy surfaces and most likely to become easier once the earlier contract bugs are resolved

## Recommended Phases

### Phase 1: Rendering-contract audit and repair

Primary proof:

- `python3 -m pytest tests/unit/test_workflows.py tests/performance/test_harness.py -k 'default_prompt_pack_load_and_render or compile_task_workflow_renders_canonical' -q`

Exit criteria:

- prompt-pack rendering no longer raises missing-variable errors for valid built-in prompts
- compiled workflow render-variable assertions are updated only if the documented contract truly changed

### Phase 2: Reproducibility snapshot repair

Primary proof:

- `python3 -m pytest tests/unit/test_reproducibility.py tests/integration/test_daemon.py -k 'run_audit' -q`
- `python3 -m pytest tests/integration/test_session_cli_and_daemon.py -k 'node_and_run_audit' -q`

Exit criteria:

- all run-audit surfaces serialize durable attempt payloads successfully
- snapshot schemas and models are aligned with durable DB fields

### Phase 3: Runtime-state and materialization semantics repair

Primary proof:

- `python3 -m pytest tests/integration/test_database_lifecycle.py tests/integration/test_daemon.py -k 'schema_compatibility or runtime_state or child_materialization' -q`
- `python3 -m pytest tests/e2e/test_flow_03_materialize_and_schedule_children_real.py -q`

Exit criteria:

- migration-status, dependency-blocker, and child-scheduling semantics agree across DB, daemon, CLI, and E2E surfaces

### Phase 4: Compile-stage diagnostics and hook-expansion repair

Primary proof:

- `python3 -m pytest tests/e2e/test_flow_19_hook_expansion_compile_stage_real.py tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py -q`
- `python3 -m pytest tests/performance/test_harness.py -k 'workflow_compile_with_hook_expansion' -q`

Exit criteria:

- compile-stage hook and failure-diagnostic outputs are deterministic and documented
- source-discovery/compile-failure behavior is consistent for failed and retried compiles

### Phase 5: Full-runtime and residual performance closure

Primary proof:

- `python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q`
- `python3 -m pytest tests/performance/test_harness.py -k 'turnkey_quality_chain or provenance_refresh_and_lookup' -q`

Exit criteria:

- the remaining real-runtime and performance defects are either fixed or narrowed to an explicitly documented external blocker

### Phase 6: Final authoritative parallel proof

Primary proof:

- `python3 -m pytest tests -n auto --dist=loadfile -q --ignore tests/integration/test_parallel_all_tests_meta.py -m "not requires_ai_provider"`
- `AICODING_ENABLE_META_PARALLEL_TEST=1 python3 -m pytest tests/integration/test_parallel_all_tests_meta.py -q`

Exit criteria:

- the remaining failure set is empty for the eligible environment, or any residual gated failure is documented honestly with no false completion claim

## Verification

Planning-target verification commands for the follow-on remediation work:

```bash
python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_workflows.py tests/performance/test_harness.py -k 'default_prompt_pack_load_and_render or compile_task_workflow_renders_canonical' -q
python3 -m pytest tests/unit/test_reproducibility.py tests/integration/test_daemon.py -k 'run_audit or schema_compatibility or child_materialization' -q
python3 -m pytest tests/integration/test_database_lifecycle.py -q
python3 -m pytest tests/integration/test_session_cli_and_daemon.py -k 'node_and_run_audit' -q
python3 -m pytest tests/e2e/test_flow_03_materialize_and_schedule_children_real.py tests/e2e/test_flow_19_hook_expansion_compile_stage_real.py tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py -q
python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q
python3 -m pytest tests/performance/test_harness.py -k 'turnkey_quality_chain or workflow_compile_with_hook_expansion or provenance_refresh_and_lookup' -q
python3 -m pytest tests -n auto --dist=loadfile -q --ignore tests/integration/test_parallel_all_tests_meta.py -m "not requires_ai_provider"
```

If implementation updates authoritative notes, rerun the affected document-family tests in the same change.

## Exit Criteria

- Every currently failing test is assigned to a remediation workstream with an explicit implementation order and justification.
- Follow-on remediation work fixes lower-layer shared root causes before adjusting higher-layer E2E expectations.
- Any intentional contract changes uncovered during remediation are reflected in notes and tests together.
- The authoritative `-n auto` parallel command is the final proving surface for the batch.
