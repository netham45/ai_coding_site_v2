# Task: Full Tree Rectification Rebuild Real E2E

## Goal

Extend the authoritative full-tree real git/runtime suite so it proves hierarchy-wide rollback/reset correctness through the real `node rectify-upstream` rebuild path after an already-merged hierarchy is modified again.

## Rationale

- Rationale: The repo already proves hierarchy-wide incremental merge propagation and now has dedicated real rectification and rebuild-coordination suites, but the checklist still calls out the missing full-tree rollback/reset narrative through `node rectify-upstream`.
- Reason for existence: This task exists to close that last FC-15 full-tree gap by proving a real task edit can force ancestor rebuild, reset stale merged content, replay current authoritative child finals, and preserve unaffected sibling contributions.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`
- `plan/features/83_F19_dependency_aware_regeneration_scope.md`
- `plan/features/84_F19_dependency_invalidated_node_fresh_rematerialization.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `plan/reconcilliation/05_full_epic_tree_git_lifecycle_expansion.md`

## Scope

- Database: rely on durable version lineage, rebuild history, and authoritative-version movement written by the real daemon path.
- CLI: prove real `git bootstrap-node`, `git finalize-node`, `node rectify-upstream`, `node rebuild-history`, `node versions`, `node version cutover-readiness`, and `node version cutover` surfaces in the hierarchy-wide path.
- Daemon: prove ancestor candidate rebuild resets stale merged content and replays current authoritative child finals through the real rectification path.
- YAML: not affected in this slice.
- Prompts: not affected in this slice.
- Tests: extend `tests/e2e/test_e2e_full_epic_tree_runtime_real.py` with a real hierarchy-wide rectify/rebuild narrative after the initial merge completes.
- Performance: keep the fixture tiny and deterministic by reusing the existing bootstrapped full-tree hierarchy pattern.
- Notes: update FC-08/FC-15 limitations and related audit text if the hierarchy-wide rollback/reset gap is actually closed.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q -k rectify
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the full-tree real suite proves a second task revision can trigger `node rectify-upstream` and rebuild plan, phase, and epic candidates from reset state
- rebuilt candidate repos contain current task content, exclude stale superseded task content, and preserve unaffected sibling contributions
- grouped cutover of the rebuilt root candidate succeeds and moves authoritative lineage to the rebuilt hierarchy
- checklist and audit surfaces no longer claim the rectification rebuild path is missing if the real proof actually passes

## Completion Notes

- Status: `verified`
- Result: `tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q -k rectify` now passes and proves the hierarchy-wide rollback/reset narrative through the real `node rectify-upstream` path after a second authoritative task revision.
- Follow-up: broader FC-15 remains `partial` outside this task because CLI/prompt/performance scope is still wider than this single full-tree git/runtime narrative.
