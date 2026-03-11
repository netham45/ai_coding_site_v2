# Task: Incremental Parent Merge Phase 02 One-Child Incremental Merge Execution

## Goal

Implement the first real daemon-owned incremental child-to-parent merge execution path so one completed-unmerged child can be merged into the parent live repo and recorded durably as success or conflict.

## Rationale

- Rationale: The phase-1 durable state substrate makes completed child merge work discoverable, but sibling visibility still does not improve until the daemon can actually mutate parent git state forward and write merge audit records.
- Reason for existence: This task exists as a separate slice so the repository can prove one-child incremental merge execution, parent-head advancement, idempotent replay, and conflict recording before changing dependency truth or child refresh semantics.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`
- `plan/features/76_F18_incremental_parent_merge_phase_02_one_child_incremental_merge_execution.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`
- `plan/features/22_F20_conflict_detection_and_resolution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/planning/implementation/live_git_merge_and_finalize_execution_decisions.md`
- `notes/planning/implementation/child_merge_and_reconcile_pipeline_decisions.md`
- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`

## Scope

- Database: persist one-child incremental merge success/conflict into durable merge-lane and per-child incremental merge state, including actual applied merge order.
- CLI: no new command family in this slice, but existing merge event and merge conflict inspection surfaces must continue to reflect the new execution path.
- Daemon: acquire a per-parent advisory lock, consume one completed-unmerged child, merge it into the parent live repo at the current lane head, and record success or conflict idempotently.
- YAML: not affected in this slice.
- Prompts: not affected in the happy path; conflict prompt handoff remains deferred.
- Tests: add bounded success/idempotency/conflict coverage plus one real git-backed merge-execution proof.
- Performance: one-child merge execution should touch only the targeted parent lane and avoid broad rescans.
- Notes: capture any doctrine adjustments needed to explain the live-git reuse path and lane-head advancement semantics.

## Plan

### Phase 2A: Task scaffolding and merge-path review

1. Add the authoritative task plan and development log entry for this phase.
2. Review the existing live-git merge path, merge-event/conflict recording helpers, and advisory-lock substrate.
3. Confirm the smallest reusable code path for one-child incremental merge execution.

Exit criteria:

- task/log artifacts exist and the implementation path is tied to existing live-git and advisory-lock code

### Phase 2B: One-child incremental merge execution

1. Add daemon helpers to lock a parent lane, select one completed-unmerged child, and execute one incremental child-to-parent merge against the current lane head.
2. Persist applied merge order, parent commit before/after, lane-head advancement, and conflict state into durable incremental merge records.
3. Ensure non-authoritative parent/child lineage is rejected or superseded instead of being merged into stale lineage.

Exit criteria:

- one completed-unmerged child can be merged upward once, with success or conflict recorded durably

### Phase 2C: Bounded proof and real git-backed proof

1. Add bounded tests for success, idempotent replay, and conflict recording.
2. Add a real git-backed unit/integration proof that the daemon-owned incremental merge path mutates the parent repo and records audit state.
3. Run the affected code and authoritative document verification commands.

Exit criteria:

- the new merge execution path is proven through bounded logic tests plus real git-backed execution proof

## Verification

- `python3 -m pytest tests/unit/test_incremental_parent_merge.py tests/unit/test_run_orchestration.py tests/unit/test_live_git.py tests/unit/test_document_schema_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`
- `git diff --check`

## Exit Criteria

- one completed child can be incrementally merged upward through daemon-owned execution
- merge success and merge conflict both update durable incremental merge state
- duplicate replay does not double-merge an already applied child
- existing merge event and merge conflict inspection surfaces still reflect the resulting audit trail
- later dependency-readiness changes remain explicitly deferred
