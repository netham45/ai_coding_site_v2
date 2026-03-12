# Task: Dependency-Invalidated Fresh Restart Real E2E

## Goal

Add a real daemon/CLI/database E2E proof for the reachable part of the dependency-invalidated fresh-restart flow: sibling dependency invalidation during regenerate/rectify must create a fresh childless dependent candidate and remap the rebuilt parent candidate to that fresh child candidate.

## Rationale

- Rationale: The bounded and integration layers now prove ancestor remap plus fresh-restart runtime behavior, but the real flow family still lacks direct proof that daemon-backed regenerate/rectify carries the fresh sibling restart into the rebuilt parent lineage.
- Reason for existence: This task exists to extend the real E2E surface for FC-15 honestly while the later candidate-to-authoritative rematerialization cutover slice is still pending.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/84_F19_dependency_invalidated_node_fresh_rematerialization.md`
- `plan/features/85_F19_version_consistent_live_runtime_authority.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/planning/implementation/regeneration_and_upstream_rectification_decisions.md`

## Scope

- Database: inspect durable node-version and node-child lineage after real daemon mutations.
- CLI: drive the scenario through real CLI commands.
- Daemon: exercise the real regenerate/rectify path and confirm the parent candidate lineage is rebuilt with the fresh dependent sibling candidate.
- Website: not applicable in this slice.
- YAML: use existing built-in layout materialization only.
- Prompts: not applicable in this slice.
- Tests: add a real E2E that proves ancestor remap plus fresh childless restart under live daemon conditions.
- Performance: keep the real proof bounded to one parent and two siblings so it exercises the live path without turning the suite into a long multi-tree rebuild narrative.
- Notes: record the new proving layer honestly without overstating the still-missing post-cutover rematerialization narrative.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_10_regenerate_and_rectify_real.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- real Flow 10 proof covers dependency-invalidated fresh restart creation and ancestor remap
- the real proof confirms the dependent fresh candidate is childless and rebound to the rebuilt parent candidate
- notes/logs/checklists reflect the stronger but still partial E2E status honestly
