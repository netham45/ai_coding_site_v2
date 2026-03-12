# Task: Incremental Parent Merge Hierarchy Full-Tree Real E2E

## Goal

Extend the authoritative full-tree real runtime suite so task -> plan -> phase -> epic git propagation happens through the daemon-owned incremental parent-merge lane instead of manual ancestor `git merge-children` steps.

## Rationale

- Rationale: The incremental parent-merge feature now has real sibling happy-path, refresh, conflict, restart, and parent-reconcile proof, but it still lacks a passing hierarchy-wide real narrative.
- Reason for existence: This task exists to convert the remaining “broader hierarchy-wide incremental merge” gap into a real full-tree runtime flow and to keep manual/no-run finalized children on the same merge-backed contract as run-completed children.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`
- `plan/features/81_F18_incremental_parent_merge_phase_07_final_parent_reconcile_redefinition.md`
- `plan/features/82_F08_F18_incremental_parent_merge_full_e2e.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/planning/implementation/child_merge_and_reconcile_pipeline_decisions.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`
- `plan/features/82_F08_F18_incremental_parent_merge_full_e2e.md`

## Scope

- Database: finalized authoritative child versions that are manually/no-run completed must seed durable completed-unmerged merge state.
- CLI: the full-tree test should continue to use existing lifecycle, git, child-results, reconcile, and merge-history surfaces.
- Daemon: ancestor propagation should happen through the background incremental merge lane after explicit child `COMPLETE` transitions.
- YAML: not affected directly in this slice.
- Prompts: not affected directly in this slice.
- Tests: rewrite the full-tree real git propagation test away from manual ancestor `git merge-children`.
- Performance: keep the hierarchy-wide wait loops bounded so the real full-tree proof remains diagnosable and does not hide daemon-lane stalls behind excessive timeouts.
- Notes: keep the runtime/lifecycle/reconcile doctrine aligned and record the current stop-point honestly if unrelated blockers prevent a passing real run.

## Verification

- `python3 -m py_compile src/aicoding/daemon/lifecycle.py tests/e2e/test_e2e_full_epic_tree_runtime_real.py`
- `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q -k git_merge_propagates`
- `PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`
- `git diff --check`

## Exit Criteria

- the full-tree real suite no longer manually merges task/plan/phase children upward through ancestor `git merge-children`
- explicit lifecycle transitions to `COMPLETE` after manual/no-run finalization seed the same incremental merge lane as ordinary run completion
- the hierarchy-wide real test proves parent reconcile surfaces read already-applied merge history after daemon-owned incremental propagation
- any blocker that prevents the passing real run is documented explicitly instead of being hidden behind a stronger status claim
