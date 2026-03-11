# Task: Incremental Parent Merge Phase 03 Merge-Backed Dependency Truth

## Goal

Change sibling dependency readiness so dependent children become ready only after prerequisite siblings have been incrementally merged into the authoritative parent lineage they will bootstrap from.

## Rationale

- Rationale: The flow bug remains until dependency truth stops collapsing to sibling lifecycle completion and instead requires merge-backed parent visibility.
- Reason for existence: This task exists as a separate slice so the repository can prove the readiness/blocker rewrite cleanly before tackling later parent-refresh and background auto-start refinements.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`
- `plan/features/77_F08_incremental_parent_merge_phase_03_merge_backed_dependency_truth.md`
- `plan/features/11_F08_dependency_graph_and_admission_control.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/64_F08_F15_richer_child_scheduling_and_blocker_explanation.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/contracts/runtime/invalid_dependency_graph_handling.md`
- `notes/pseudocode/modules/check_node_dependency_readiness.md`
- `notes/pseudocode/state_machines/node_lifecycle.md`
- `notes/planning/implementation/dependency_graph_and_admission_control_decisions.md`
- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`

## Scope

- Database: continue using durable blocker rows and incremental merge state as the readiness source of truth; no new dependency table is required in this slice.
- CLI: existing blocker and dependency-status surfaces must expose the richer merge-backed blocker kinds.
- Daemon: sibling dependency satisfaction must require incremental merge success; child dependencies outside the sibling case remain lifecycle-based for now.
- YAML: not affected in this slice.
- Prompts: not affected directly in this slice.
- Tests: add bounded blocker-transition proof and one integration proof that sibling completion alone no longer admits a dependent node.
- Performance: readiness recomputation should stay local to dependency and incremental-merge state reads.
- Notes: update the parent/child scheduling and dependency implementation notes to reflect merge-backed sibling truth explicitly.

## Plan

### Phase 3A: Task scaffolding and readiness review

1. Add the authoritative task plan and development log entry for this phase.
2. Review current dependency-readiness, blocker persistence, and operator read surfaces.
3. Confirm the smallest repo-native readiness rewrite that reuses existing blocker storage and CLI reads.

Exit criteria:

- task/log artifacts exist and the readiness rewrite is tied to the current blocker/admission path

### Phase 3B: Merge-backed sibling dependency rewrite

1. Update dependency readiness so sibling dependencies require a successful incremental merge row instead of raw target lifecycle completion.
2. Add richer blocker kinds for unmerged and conflicted prerequisite siblings.
3. Keep child and non-sibling dependency semantics stable unless the dependency edge specifically requires sibling merge-backed visibility.

Exit criteria:

- sibling completion alone no longer makes dependents ready

### Phase 3C: Bounded and integration proof

1. Add unit coverage for blocker transitions from `blocked_on_dependency` to `blocked_on_incremental_merge` to `ready`.
2. Add integration proof that a dependent sibling cannot start after prerequisite completion alone and can start after incremental merge success.
3. Run the affected code and authoritative document verification commands.

Exit criteria:

- the merge-backed sibling dependency truth is proven in admission/blocker behavior and real daemon admission flow

## Verification

- `python3 -m pytest tests/unit/test_admission.py tests/unit/test_incremental_parent_merge.py tests/integration/test_dependency_flow.py tests/unit/test_document_schema_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`
- `git diff --check`

## Exit Criteria

- sibling dependency readiness depends on successful incremental merge state
- blocker rows and existing dependency-status/blocker surfaces expose the richer waiting reasons
- sibling completion alone no longer admits dependents
- later parent-refresh and background auto-start behavior remains explicitly deferred
