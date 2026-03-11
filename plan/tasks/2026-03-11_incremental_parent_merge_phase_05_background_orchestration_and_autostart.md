# Task: Incremental Parent Merge Phase 05 Background Orchestration And Autostart

## Goal

Wire the daemon background loop so completed child merges, stale-child refresh, and child auto-start happen automatically on the happy path without parent AI intervention.

## Rationale

- Rationale: The earlier phases added durable merge state, one-child merge execution, merge-backed dependency truth, and explicit child refresh, but operators still need the daemon to run those steps continuously.
- Reason for existence: This task exists as a separate slice so the repository can prove the background daemon path owns incremental parent merge progression while the existing child auto-start loop stays narrow.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`
- `plan/features/79_F09_incremental_parent_merge_phase_05_background_orchestration_and_autostart.md`
- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/77_F08_incremental_parent_merge_phase_03_merge_backed_dependency_truth.md`
- `plan/features/78_F15_incremental_parent_merge_phase_04_dependent_child_parent_refresh.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/planning/implementation/dependency_graph_and_admission_control_decisions.md`
- `notes/planning/implementation/live_git_merge_and_finalize_execution_decisions.md`
- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`

## Scope

- Database: use durable merge-lane state, child merge rows, and dependency blockers as the authoritative background-loop truth.
- CLI: existing dependency/blocker and child-result reads should reflect the background loop’s merged-upward and refreshed-child effects without new commands in this slice.
- Daemon: process pending parent merge lanes during background ticks, refresh stale not-yet-started children, and keep session binding limited to already-ready children.
- YAML: not affected in this slice.
- Prompts: no new happy-path parent prompts in this slice; ordinary background progression stays daemon-owned.
- Tests: add bounded proof for the new pre-pass and integration proof that the daemon background loop can merge upward, refresh a stale dependent child, and then auto-start it.
- Performance: background work should remain a cheap repeated scan over pending lanes plus auto-run child candidates.
- Notes: document that the child auto-start loop now has a daemon-owned pre-pass for incremental merge and parent-refresh advancement.

## Plan

### Phase 5A: Task scaffolding and loop review

1. Add the authoritative task plan and development log entry for this phase.
2. Review the current daemon background loop and existing child auto-start path.
3. Confirm the smallest repo-native insertion point for merge-lane processing and child refresh.

Exit criteria:

- the task/log artifacts exist and the phase is tied to the current background loop in `app.py`

### Phase 5B: Background pre-pass wiring

1. Add a daemon helper that processes pending parent incremental merge lanes and refreshes stale auto-run children before session binding.
2. Wire that helper into the existing child auto-start background loop ahead of `auto_bind_ready_child_runs(...)`.
3. Keep the session-binding function itself limited to already-ready children.

Exit criteria:

- the daemon background loop advances merge lanes and stale-child refresh before attempting child auto-start

### Phase 5C: Bounded and integration proof

1. Add bounded proof that the new background pre-pass invokes pending merge processing and stale-child refresh without widening the bind loop.
2. Add integration proof that a dependent child only auto-starts after the daemon background loop merges its prerequisite sibling upward and refreshes the child bootstrap.
3. Run the affected code and authoritative document verification commands.

Exit criteria:

- the daemon-owned happy path is proven at bounded and integration layers for this slice

## Verification

- `python3 -m pytest tests/unit/test_session_records.py::test_auto_advance_incremental_parent_merge_and_refresh_children_runs_merge_prepass_and_refreshes_stale_children tests/unit/test_incremental_parent_merge.py -q`
- `python3 -m pytest tests/integration/test_daemon.py::test_background_child_auto_run_loop_blocks_simple_chain_until_dependency_completes tests/integration/test_daemon.py::test_background_child_auto_run_loop_unblocks_fan_out_siblings_together_after_shared_prerequisite tests/integration/test_daemon.py::test_background_child_auto_run_loop_starts_independent_siblings_while_leaving_dependent_third_blocked -q`
- `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`
- `git diff --check`

## Exit Criteria

- the background daemon loop processes pending parent incremental merge work before child session auto-bind
- stale auto-run children blocked on `blocked_on_parent_refresh` can be refreshed automatically before auto-start
- `auto_bind_ready_child_runs(...)` remains a ready-child-only binding path
- the phase is implemented and bounded/integration verified, with full real E2E still tracked separately
