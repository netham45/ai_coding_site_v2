# Task: Incremental Parent Merge Phase 04 Dependent Child Parent Refresh

## Goal

Detect stale child bootstrap ancestry relative to the parent incremental-merge lane head and provide a daemon-owned refresh path that clears the blocker before the child starts.

## Rationale

- Rationale: Merge-backed readiness alone is still insufficient if a dependent child already has a stale bootstrap seed from an older parent head.
- Reason for existence: This task exists as a separate slice so the repository can prove durable stale-bootstrap detection and explicit child refresh semantics before wiring refresh into the later background auto-start loop.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`
- `plan/features/78_F15_incremental_parent_merge_phase_04_dependent_child_parent_refresh.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`
- `plan/features/77_F08_incremental_parent_merge_phase_03_merge_backed_dependency_truth.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/planning/implementation/live_git_merge_and_finalize_execution_decisions.md`
- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`

## Scope

- Database: use durable child bootstrap seed and parent merge-lane head as the stale-bootstrap truth in this slice.
- CLI: existing blocker/materialization surfaces must expose `blocked_on_parent_refresh`.
- Daemon: detect stale child bootstrap ancestry and provide an explicit refresh helper that reboots the child repo onto the current parent head before run admission.
- YAML: not affected in this slice.
- Prompts: not affected directly in this slice.
- Tests: add bounded stale-bootstrap detection and refresh-clearance coverage plus one real git-backed proof that refreshed children inherit the updated parent head.
- Performance: refresh checks should remain local to child seed state and parent lane head lookups.
- Notes: document the current refresh invariant and the explicit pre-run child seed rewrite.

## Plan

### Phase 4A: Task scaffolding and bootstrap review

1. Add the authoritative task plan and development log entry for this phase.
2. Review child bootstrap, live-git seed handling, and scheduling surfaces.
3. Confirm the smallest repo-native refresh contract that fits the current implementation.

Exit criteria:

- task/log artifacts exist and the refresh contract is tied to the current live-git bootstrap path

### Phase 4B: Stale-bootstrap detection and explicit refresh helper

1. Extend admission/readiness so merge-satisfied sibling dependencies still block on `blocked_on_parent_refresh` when the child seed is behind the parent lane head.
2. Add a daemon helper to replace the child repo bootstrap at the current parent lane head and update the child seed accordingly before first run.
3. Expose the new blocker through existing scheduling/materialization reads.

Exit criteria:

- stale child bootstrap is admission-blocking and an explicit refresh helper can clear it

### Phase 4C: Bounded and real git-backed proof

1. Add unit coverage for stale-bootstrap blocker detection and refresh clearance.
2. Add one real git-backed proof that a refreshed child inherits the updated parent head after prerequisite merge.
3. Run the affected code and authoritative document verification commands.

Exit criteria:

- the refresh contract is proven through readiness/blocker behavior and real bootstrap refresh behavior

## Verification

- `python3 -m pytest tests/unit/test_admission.py tests/unit/test_live_git.py tests/unit/test_incremental_parent_merge.py tests/unit/test_materialization.py tests/unit/test_document_schema_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`
- `git diff --check`

## Exit Criteria

- dependent children with stale bootstrap ancestry are blocked by `blocked_on_parent_refresh`
- a daemon-owned refresh helper can clear the stale bootstrap blocker before run admission
- existing scheduling/materialization reads expose the new blocker
- later background auto-refresh wiring remains explicitly deferred
