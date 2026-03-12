# Task: Dependency-Invalidated Fresh Rematerialization Implementation

## Goal

Implement the first daemon/runtime slice of dependency-invalidated fresh rematerialization so a sibling invalidated by regenerated prerequisite work gets a fresh childless candidate version and stays blocked instead of returning to `READY`.

## Rationale

- Rationale: The current supersession path clones child structure forward, which silently preserves stale dependent subtrees across sibling invalidation.
- Reason for existence: This task exists to replace that reuse with a fresh blocked restart path before later work wires the full post-refresh rematerialization flow.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/78_F15_incremental_parent_merge_phase_04_dependent_child_parent_refresh.md`
- `plan/features/84_F19_dependency_invalidated_node_fresh_rematerialization.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/pseudocode/modules/regenerate_node_and_descendants.md`
- `notes/planning/implementation/regeneration_and_upstream_rectification_decisions.md`

## Scope

- Database: reuse the existing version-scoped child-edge model, but ensure dependency-invalidated fresh candidates do not clone those edges forward.
- CLI: no new command family in this slice, but rebuild history and lifecycle reads should remain coherent for blocked fresh-restart candidates.
- Daemon: add fresh supersede without cloned structure, reverse sibling invalidation detection, and blocked lifecycle placement for invalidated dependents.
- YAML: not applicable in this slice.
- Prompts: no new prompt assets in this slice.
- Tests: add bounded coverage for fresh childless dependent candidates and blocked-after-reset behavior.
- Performance: keep reverse sibling invalidation lookup narrow and authoritative-version-based.
- Notes: update regeneration and child-materialization doctrine to describe the fresh blocked restart rule explicitly.

## Planned Changes

1. Add a fresh-supersede option in versioning that skips cloning version-scoped child structure.
2. Extend regeneration to identify reverse sibling dependents and use fresh supersede for them.
3. Place dependency-invalidated dependents into `WAITING_ON_SIBLING_DEPENDENCY` rather than `READY`.
4. Update the relevant implementation notes and checklist mapping.
5. Add focused unit coverage and run the targeted bounded/document tests.

## Verification

Canonical verification commands for this task:

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_node_lifecycle.py tests/unit/test_regeneration.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- dependency-invalidated fresh candidates do not clone old child edges
- invalidated dependents reset into `WAITING_ON_SIBLING_DEPENDENCY` instead of `READY`
- bounded tests prove the childless fresh-restart behavior
- notes, checklist mapping, and development log are updated honestly for the implemented slice
