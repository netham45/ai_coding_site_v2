# Phase 02 Draft: One-Child Incremental Merge Execution

## Goal

Process one completed child into parent state and persist merge success or conflict durably.

## Rationale

- Rationale: Durable completed-unmerged state alone does not fix sibling visibility; the daemon must be able to consume one completed child and mutate parent state forward in a controlled, auditable way.
- Reason for existence: This phase exists to establish the smallest real child-to-parent incremental merge execution path before dependency truth and child refresh semantics are changed.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`: this phase narrows F18 into a daemon-owned one-child incremental merge path rather than the later all-children reconcile stage.
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`: real git merge behavior should reuse and extend the existing live-git execution model.
- `plan/features/12_F17_deterministic_branch_model.md`: branch and commit anchors remain critical for replayable parent-head transitions.
- `plan/features/22_F20_conflict_detection_and_resolution.md`: conflict records discovered here will later feed the parent AI conflict path.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/planning/implementation/live_git_merge_and_finalize_execution_decisions.md`
- `notes/planning/implementation/child_merge_and_reconcile_pipeline_decisions.md`
- `plan/future_plans/sibling_dependency_incremental_parent_merge/2026-03-11_overview.md`

## Scope

- Database: persist parent commit transitions, one-child incremental merge success/conflict state, replay-safe merge audit, and actual applied incremental merge order.
- CLI: not yet a full operator surface phase, but merge state should remain inspectable enough for debugging and later operator reads.
- Daemon: scan one completed-unmerged child for a locked parent, execute one incremental child-to-parent merge, and record success or conflict.
- YAML: no new YAML semantics in this phase; merge legality stays code-owned.
- Prompts: no ordinary prompt changes in the happy path; conflict prompt work belongs to a later phase.
- Tests: bounded one-child merge success, duplicate scan idempotency, and conflict recording, plus real git-backed merge execution proof.
- Performance: one-child merge execution should remain bounded and deterministic enough for repeated background use.
- Notes: update git/runtime doctrine to distinguish one-child incremental merge execution from the later full parent reconcile stage, and define how superseded child or parent lineage prevents stale incremental merge application.

## Verification

- Bounded proof:
  - one-child merge success path
  - duplicate background scans do not double-merge
  - conflict path records durable conflict state
- Real proof:
  - real git-backed parent/child repos prove one completed child merges upward through daemon-owned execution

## Exit Criteria

- one completed child can be merged upward through daemon-owned execution
- success and conflict are both persisted durably
- later dependency-readiness and child-refresh semantics are still explicitly deferred
- this phase remains a future-plan draft and is not an implementation claim by itself
