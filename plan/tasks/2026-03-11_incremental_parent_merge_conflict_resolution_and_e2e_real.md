# Task: Incremental Parent Merge Conflict Resolution And Real E2E

## Goal

Finish the incremental parent-merge conflict-resolution runtime path so a resolved conflict actually advances merge-backed dependency truth, then prove that path through a real daemon/CLI/git end-to-end test.

## Rationale

- Rationale: The repository already persists incremental merge conflicts and parent-facing conflict context, but the current `resolve_conflict` path only updates durable conflict metadata and does not yet resume the incremental merge lane.
- Reason for existence: This task exists to close that runtime gap before adding the next real E2E checkpoint, so the conflict narrative proves the actual supported operator/AI resolution path instead of a placeholder status change.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`
- `plan/features/80_F20_incremental_parent_merge_phase_06_conflict_handoff_and_prompt_context.md`
- `plan/features/82_F08_F18_incremental_parent_merge_full_e2e.md`
- `plan/features/22_F20_conflict_detection_and_resolution.md`
- `plan/features/72_F13_expanded_human_intervention_matrix.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/planning/implementation/conflict_detection_and_resolution_decisions.md`
- `notes/planning/implementation/expanded_human_intervention_matrix_decisions.md`
- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`
- `plan/features/82_F08_F18_incremental_parent_merge_full_e2e.md`

## Scope

- Database: update durable incremental child merge state, merge event history, lane state, and conflict resolution metadata when a conflicted incremental merge is manually resolved.
- CLI: continue to use existing `git merge-conflicts resolve`, `node interventions`, `node intervention-apply`, `node blockers`, `node dependency-status`, `node child-results`, `node reconcile`, and `subtask context` surfaces.
- Daemon: when a resolved conflict belongs to an incremental merge lane, verify the parent repo is actually resolved, promote that child merge row from `conflicted` to `merged`, advance the lane head, and allow dependent refresh/unblock on the next daemon pass.
- YAML: not affected directly in this slice.
- Prompts: keep parent conflict handoff daemon-assembled through existing `parent_reconcile_context`; update the notes so resolution now means runtime progression is possible rather than only metadata change.
- Tests: add bounded proof for incremental conflict resolution bookkeeping and add a real E2E conflict handoff/resolution narrative.
- Performance: keep resolution bookkeeping local to one parent lineage and one conflicted child row.
- Notes: update the conflict, CLI, runtime, and incremental-parent-merge doctrine so the implemented semantics match the real runtime path.

## Plan

### Phase CR-A: Runtime-gap closure

1. Add the authoritative task plan and development log.
2. Review the current incremental merge conflict bookkeeping and the existing operator resolution surfaces.
3. Define the repo-native resolution contract: operator/AI resolves the parent repo, commits the merge, then records durable resolution through the existing CLI/intervention path.

Exit criteria:

- the runtime gap is stated explicitly and tied to the repo's existing CLI/daemon surfaces

### Phase CR-B: Conflict-resolution bookkeeping

1. Extend durable conflict resolution so incremental merge conflicts validate the parent repo is actually resolved and committed before accepting `resolution_status = resolved`.
2. Promote the affected incremental child merge row from `conflicted` to `merged`, update the merge event's `parent_commit_after`, and advance the parent incremental merge lane head/status.
3. Preserve parent-facing conflict context and refresh it so inspectable status shows both the resolved conflict record and the lane's new state.

Exit criteria:

- resolving an incremental merge conflict advances the authoritative parent lane instead of only updating a conflict row

### Phase CR-C: Real E2E proof and note alignment

1. Add a real daemon/CLI/git E2E narrative where one child merges successfully, a second child conflicts, a dependent third child stays blocked, the conflict is manually resolved in the parent repo, and the dependent child only unblocks after durable resolution.
2. Update the incremental parent-merge E2E plan, feature checklist, command catalog, feature matrix, and applicable doctrine notes.
3. Run the targeted bounded, real-E2E, and authoritative document verification commands.

Exit criteria:

- the real conflict handoff/resolution path is proven through the actual project surfaces and documented honestly

## Verification

- `PYTHONPATH=src python3 -m pytest tests/unit/test_incremental_parent_merge.py tests/unit/test_git_conflicts.py -q`
- `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q`
- `PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`
- `git diff --check`

## Exit Criteria

- resolving an incremental merge conflict updates the affected merge row, merge event, and parent lane using the actual resolved parent repo head
- the parent and dependent-child inspection surfaces reflect the resumed merge-backed truth after durable resolution
- a real daemon/CLI/git E2E proves conflict handoff, manual resolution, and dependent-child unblock on the implemented path
- restart and broader hierarchy conflict narratives remain explicitly deferred if not proven in this slice
