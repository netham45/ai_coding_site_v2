# Task: Dependency-Invalidated Fresh Rematerialization Follow-On

## Goal

Finish the next F19 slice so dependency-invalidated sibling fresh candidates are carried into upstream rectification correctly, refresh from updated parent truth after prerequisite merge progress, and only become runnable after fresh child rematerialization from an empty tree.

## Rationale

- Rationale: The current runtime already creates a fresh blocked dependent candidate, but upstream rectification can still omit that candidate from ancestor rebuilds and the later refresh/rematerialization path is not wired end to end.
- Reason for existence: This task exists to close the remaining gap between fresh dependency-invalidated restart creation and the later parent-refresh-plus-rematerialization behavior promised by the feature plan.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/78_F15_incremental_parent_merge_phase_04_dependent_child_parent_refresh.md`
- `plan/features/84_F19_dependency_invalidated_node_fresh_rematerialization.md`
- `plan/features/85_F19_version_consistent_live_runtime_authority.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/pseudocode/modules/regenerate_node_and_descendants.md`
- `notes/planning/implementation/regeneration_and_upstream_rectification_decisions.md`
- `notes/planning/implementation/live_rebuild_cutover_coordination_decisions.md`

## Scope

- Database: preserve historical child trees on superseded versions, but ensure fresh dependency-invalidated restart metadata is inspectable and later refresh/rematerialization targets the fresh version only.
- CLI: existing rebuild-history, version, lifecycle, and materialization surfaces should expose the fresh restart and later rematerialization outcome without adding a new command family.
- Daemon: carry dependency-invalidated fresh candidates into ancestor candidate remap, keep them blocked until prerequisite merge/refresh/rematerialization completes, and drive the refresh/rematerialization follow-on through existing runtime hooks.
- Website: not directly changed in this slice; daemon-backed inspection surfaces must remain consistent for later UI consumers.
- YAML: not applicable in this slice.
- Prompts: no new prompt assets in this slice.
- Tests: add bounded, integration, and real E2E proof that the fresh dependent candidate is used consistently and rematerializes from an empty tree before becoming runnable.
- Performance: avoid turning upstream rectification into a full unrelated sibling sweep; only remap explicitly invalidated siblings discovered by the rebuild pass.
- Notes: update the rectification and child-materialization doctrine to match the implemented end-to-end behavior.

## Planned Changes

1. Extend regeneration snapshots and ancestor rectification inputs so dependency-invalidated fresh candidates are included when rebuilding ancestor candidates.
2. Wire the post-merge follow-on so a dependency-invalidated fresh node refreshes from the updated parent head and rematerializes children from an empty tree instead of remaining a dead blocked candidate.
3. Keep the fresh dependent node blocked until rematerialization plus readiness re-check clear; refresh alone must not silently mark it runnable if required structure is still missing.
4. Update the relevant notes, checklist mapping, and development log entries to reflect the implemented runtime behavior and remaining gaps honestly.
5. Add targeted bounded, integration, and real E2E coverage for the fixed path and run the documented verification commands.

## Verification

Canonical verification commands for this task:

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_regeneration.py tests/unit/test_session_records.py tests/unit/test_materialization.py -q
PYTHONPATH=src python3 -m pytest tests/integration/test_node_versioning_flow.py tests/integration/test_session_cli_and_daemon.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_10_regenerate_and_rectify_real.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- dependency-invalidated fresh sibling candidates are not omitted from ancestor rectification inputs
- the dependent fresh version refreshes from updated parent truth and rematerializes children from an empty tree through real runtime code paths
- reset/refresh do not make the dependent version runnable before rematerialization and readiness checks clear
- bounded, integration, and real E2E proof exist for the implemented scope
- notes, checklist mapping, and development log are current and accurate
