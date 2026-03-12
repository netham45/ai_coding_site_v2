# Task: Dependency-Invalidated Manual Restart Real E2E

## Goal

Prove through the real CLI/daemon/git path that a dependency-invalidated fresh restart with prior manual child authority stays blocked after parent refresh and only clears `child_tree_rebuild_required` after one of the explicit fresh-version manual rebuild actions.

## Rationale

- Rationale: Bounded and integration tests already proved the manual/hybrid rebuild gate and its explicit unblock path, but the feature remained partial because that path had not yet been exercised through real grouped cutover and real prerequisite merge progression.
- Reason for existence: This task exists to move the manual/hybrid dependency-invalidated restart path from daemon/API proof to real runtime proof in the incremental-parent-merge E2E family.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/65_F04_layout_replacement_and_hybrid_reconciliation.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`
- `plan/features/78_F15_incremental_parent_merge_phase_04_dependent_child_parent_refresh.md`
- `plan/features/84_F19_dependency_invalidated_node_fresh_rematerialization.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/contracts/parent_child/manual_vs_auto_tree_interaction.md`
- `notes/planning/implementation/regeneration_and_upstream_rectification_decisions.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`

## Scope

- Database: rely on durable rebuild, lineage, lifecycle, child authority, and dependency blocker state across real grouped cutover and follow-on merge progression.
- CLI: prove the shipped `node child create`, `node reconcile-children`, `node child-reconciliation`, `node dependency-status`, `node version cutover`, and `git finalize-node` surfaces on the real subprocess path.
- Daemon: prove the real blocked-after-refresh contract for manual dependency-invalidated fresh restarts and both explicit fresh-version unblock paths: `preserve_manual` and fresh manual child creation.
- YAML: no new declarative behavior is introduced in this slice.
- Prompts: not applicable in this slice.
- Tests: add a real incremental-parent-merge E2E covering the manual dependency-invalidated restart path after grouped cutover.
- Performance: keep the real proof inside the existing incremental-parent-merge suite instead of creating another long standalone family.
- Notes: align feature/checklist/matrix/log status with the new real proof and any remaining limitation.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q -k "manual_restart_requires_explicit_reconcile or manual_restart_clears_after_fresh_manual_child_create"
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the real incremental-parent-merge suite proves a prior-manual dependent sibling stays blocked on `child_tree_rebuild_required` after grouped cutover and real prerequisite merge progression
- the real suite proves both explicit unblock branches on the fresh version: `node reconcile-children --decision preserve_manual` on the empty fresh version and fresh `node child create ...` on that version
- notes, feature status, E2E matrix, and development logs are updated honestly
