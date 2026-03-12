# Task: Dependency-Invalidated Authoritative Follow-On Real E2E Planning

## Goal

Move the remaining real proof for dependency-invalidated fresh rematerialization onto a flow that actually drives prerequisite sibling completion and parent-merge progression, instead of overloading Flow 10 with a path it cannot currently reach.

## Rationale

- Rationale: The grouped cutover follow-on slice now works at bounded and integration layers, but the attempted real Flow 10 proof showed that Flow 10 does not produce the prerequisite merge progression needed for a dependency-invalidated authoritative child to become `blocked_on_parent_refresh` and rematerialize.
- Reason for existence: This task exists to document the correct real proving target before more implementation or E2E work is attempted, so the repository does not keep aiming the remaining FC-15 gap at the wrong runtime narrative.

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
- `notes/planning/implementation/regeneration_and_upstream_rectification_decisions.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`

## Scope

- Database: no schema change in this planning slice.
- CLI: identify which existing real CLI flow can exercise prerequisite merge progression for the dependency-invalidated child.
- Daemon: document the already-discovered runtime seam between grouped cutover and authoritative post-cutover rematerialization.
- YAML: not applicable in this slice.
- Prompts: not applicable in this slice.
- Tests: point the remaining real E2E gap at the incremental-parent-merge suite rather than Flow 10 alone.
- Performance: not applicable in this planning slice.
- Notes: update feature progress and checklist text so the remaining real gap is described against the correct host suite.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- FC-15 notes and plans explicitly state that the remaining real proof depends on prerequisite merge progression
- the repository no longer implies that Flow 10 alone is sufficient to prove the remaining post-cutover rematerialization path
- the next real E2E target is documented honestly before more product changes are attempted
