# Phase 01 Draft: Durable Merge Lane Scaffolding

## Goal

Add the durable coordination substrate for parent incremental merge processing without yet changing dependency-readiness semantics.

## Rationale

- Rationale: Incremental merge-backed sibling orchestration cannot be restart-safe or inspectable unless completed-child merge work is represented durably instead of being inferred from transient background scans.
- Reason for existence: This phase exists to create the parent merge-lane records, completed-unmerged child state, and background-scan discovery path that later phases will rely on for real merge execution and dependency truth.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/11_F08_dependency_graph_and_admission_control.md`: the later dependency-truth rewrite must consume durable merge-lane state instead of raw child lifecycle alone.
- `plan/features/13_F09_node_run_orchestration.md`: child completion is detected through the node-run orchestration path.
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`: this draft phase creates the durable substrate that later incremental merge execution will build on.
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`: the later merge lane will eventually drive real git mutation through the live-git layer.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/pseudocode/modules/collect_child_results.md`
- `plan/future_plans/sibling_dependency_incremental_parent_merge/2026-03-11_overview.md`

## Scope

- Database: add durable per-parent merge-lane state and per-child completed-unmerged merge records or equivalent coordination artifacts.
- CLI: not yet a primary focus, but operator inspection must eventually be able to see pending merge-lane truth once it exists.
- Daemon: detect successful child completion and write durable completed-unmerged merge state without yet changing child readiness.
- YAML: no declarative behavior change in this phase; policy remains unchanged while the runtime substrate lands.
- Prompts: no active prompt-flow change in this phase; the work is coordination-oriented.
- Tests: bounded durable-state/idempotency coverage plus real DB-backed proof that child completion writes durable completed-unmerged merge state.
- Performance: completed-child state writes and lane-state updates should remain cheap enough to run on every successful child completion.
- Notes: update database/runtime doctrine so merge-lane coordination is explicit before later phases depend on it.

## Verification

- Bounded proof:
  - child completion marks exactly one completed-unmerged parent merge record
  - repeated completion or replay does not create duplicate merge state
  - parent merge-lane state survives restart/reload
- Real proof:
  - a real daemon + database path shows a completed child creates durable completed-unmerged parent incremental-merge state

## Exit Criteria

- durable merge-lane substrate exists
- child completion can make parent merge work discoverable restart-safely
- no dependency-readiness or child-bootstrap behavior changes are claimed yet
- this phase remains a future-plan draft and is not an implementation claim by itself
