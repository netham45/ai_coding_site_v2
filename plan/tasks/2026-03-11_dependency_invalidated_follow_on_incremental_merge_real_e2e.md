# Task: Dependency-Invalidated Follow-On Incremental Merge Real E2E

## Goal

Add a real daemon/CLI/git/database E2E proving that, after grouped cutover makes a dependency-invalidated fresh restart authoritative, real prerequisite sibling completion and parent-merge progression drive the blocked child through parent refresh and fresh child rematerialization.

## Rationale

- Rationale: Flow 10 proves the reachable regenerate/rectify and grouped-cutover checkpoints, but it does not create the prerequisite merge progression needed for the authoritative follow-on rematerialization path.
- Reason for existence: This task exists to prove the remaining FC-15 runtime story in the only suite family that already drives real parent-merge advancement and dependent-child refresh behavior.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/70_F19_live_rebuild_cutover_coordination.md`
- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`
- `plan/features/78_F15_incremental_parent_merge_phase_04_dependent_child_parent_refresh.md`
- `plan/features/79_F09_incremental_parent_merge_phase_05_background_orchestration_and_autostart.md`
- `plan/features/84_F19_dependency_invalidated_node_fresh_rematerialization.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/planning/implementation/live_rebuild_cutover_coordination_decisions.md`
- `notes/planning/implementation/regeneration_and_upstream_rectification_decisions.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`

## Scope

- Database: inspect authoritative selectors, node children, and version status after grouped cutover plus follow-on rematerialization.
- CLI: drive the scenario through real `node rectify-upstream`, `node version cutover-readiness`, `node version cutover`, `git bootstrap-node`, `git finalize-node`, `node run start`, `node dependency-status`, `node children`, and `node lifecycle show` commands.
- Daemon: exercise the grouped follow-on cutover path plus the authoritative background refresh/rematerialization loop.
- YAML: rely on existing built-in layouts for the dependent child tree.
- Prompts: not applicable in this slice.
- Tests: extend the real incremental-parent-merge suite with a dependency-invalidated grouped-cutover checkpoint that waits for authoritative rematerialization after real merge progression.
- Performance: keep the real proof bounded to one parent and two sibling phases so it isolates the follow-on rematerialization contract.
- Notes: update FC-15 progress if the real proof lands, or record the exact remaining runtime blocker honestly if it does not.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q -k dependency_invalidated
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- real incremental-parent-merge flow proves grouped cutover can make the fresh dependent authoritative
- real prerequisite sibling completion advances the parent head and drives the authoritative dependent into refresh/rematerialization
- real operator surfaces show the fresh dependent receives a new child tree from empty structure rather than reusing old child ids
- notes, checklist, and development log are updated honestly for the resulting proving level
