# Task: Incremental Parent Merge Phase 07 Final Parent Reconcile Redefinition

## Goal

Redefine final parent reconcile so it consumes already-applied incremental child merge history and persists parent-local reconcile context without recording duplicate child merge events.

## Rationale

- Rationale: If final parent reconcile still synthesizes its own child merge order and records new merge events, the incremental parent-merge design remains internally contradictory.
- Reason for existence: This task exists as a separate slice so the repo can prove that post-merge parent reconcile now reads durable child merge history instead of acting as a second merge engine.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`
- `plan/features/81_F18_incremental_parent_merge_phase_07_final_parent_reconcile_redefinition.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`
- `plan/features/69_F21_F22_F23_F29_turnkey_quality_gate_finalize_chain.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/pseudocode/modules/collect_child_results.md`
- `notes/pseudocode/modules/rectify_node_from_seed.md`
- `notes/planning/implementation/child_merge_and_reconcile_pipeline_decisions.md`
- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`

## Scope

- Database: reuse durable `merge_events` and incremental merge state as the authoritative child-merge history for final reconcile rather than generating a second synthetic history.
- CLI: keep the existing `node child-results` and `node reconcile` surfaces, but make their merge-order and merge-event output reflect already-applied incremental merges.
- Daemon: remove the old final-reconcile merge execution path, require merged-upward child history before reconcile-ready, and persist parent-local reconcile context without duplicate merge-event writes.
- YAML: not directly affected in this slice.
- Prompts: the reconcile prompt path stays the same, but its runtime meaning becomes post-merge parent-local synthesis.
- Tests: add bounded proof that child-results and reconcile surfaces read existing merge history and that final reconcile does not append duplicate merge events.
- Performance: final reconcile should read current parent-version merge history directly and avoid rebuilding synthetic child merge order.
- Notes: update runtime/git/pseudocode/implementation doctrine so the written model matches the new reconcile semantics.

## Plan

### Phase 7A: Task scaffolding and reconcile-path review

1. Add the authoritative task plan and development log entry for this phase.
2. Review `child_reconcile.py`, `regeneration.py`, and the existing reconcile tests for assumptions that final reconcile still performs merge execution.
3. Confirm the smallest change that keeps existing inspection surfaces stable while removing duplicate merge-event recording.

Exit criteria:

- the task/log artifacts exist and the old reconcile merge-engine assumptions are enumerated before code changes

### Phase 7B: Durable-history-based reconcile

1. Rework child result collection so child `merge_order` comes from durable merge history already recorded for the current parent version.
2. Make final reconcile readiness depend on merged-upward child history instead of synthetic merge ordering.
3. Update `inspect_parent_reconcile(...)` and `execute_child_merge_pipeline(...)` to return existing merge events and persist reconcile context without creating new ones.

Exit criteria:

- final reconcile surfaces show already-applied child merge history and executing reconcile does not create duplicate merge events

### Phase 7C: Doctrine and bounded proof

1. Update the relevant runtime/git/prompt/pseudocode/implementation notes to describe final reconcile as post-merge parent-local synthesis.
2. Add bounded proof for:
   - child results reading actual merge order from durable merge history
   - blocked reconcile state before incremental merge has happened
   - execute-child-merge-pipeline persisting reconcile context without appending merge events
3. Run the affected code and authoritative document verification commands.

Exit criteria:

- the new reconcile doctrine is written down, bounded proof exists, and the task is documented honestly as still pending full real E2E

## Verification

- `PYTHONPATH=src python3 -m pytest tests/unit/test_child_reconcile.py tests/unit/test_incremental_parent_merge.py tests/integration/test_daemon.py::test_child_result_and_reconcile_endpoints_report_and_record_merge_state tests/integration/test_session_cli_and_daemon.py::test_cli_child_results_and_reconcile_round_trip -q`
- `PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`
- `git diff --check`

## Exit Criteria

- final parent reconcile reads already-applied child merge history for the current parent lineage
- `node child-results` and `node reconcile` no longer rely on synthetic final-stage merge ordering
- executing the child-merge pipeline persists post-merge parent reconcile context without recording duplicate merge events
- full real E2E proof for the broader incremental parent-merge narrative remains explicitly deferred
