# Task: Dependency-Invalidated Fresh Rematerialization Planning

## Goal

Author an explicit feature plan for the stricter dependency invalidation model where a dependent sibling restarts from a fresh node version with no reused child tree after a prerequisite sibling is regenerated.

## Rationale

- Rationale: The previously discussed dependency-aware rebuild-scope fix still allowed structural reuse, but the intended runtime contract is stricter: a dependency-invalidated node should restart cleanly and rematerialize children from nothing.
- Reason for existence: This task exists to capture that stricter contract as an authoritative feature slice before code changes drift toward partial reuse semantics.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
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

- Database: no schema change in this planning pass, but the feature plan must state the version-owned child-tree reset rule clearly.
- CLI: no direct CLI change in this planning pass, but the feature plan must preserve inspection expectations for fresh restart versus reused structure.
- Daemon: define the missing fresh-supersede, post-refresh rematerialization, and stale-structure rejection behavior.
- YAML: no direct YAML change in this planning pass, and the plan must keep orchestration authority in code.
- Prompts: define the prompt/runtime implications without overcommitting to new prompt assets yet.
- Tests: define bounded, integration, and real E2E proof for the fresh-rematerialization rule.
- Performance: identify likely query and rematerialization costs.
- Notes: add the authoritative feature plan and record this planning work in the development log.

## Planned Changes

1. Add a feature plan under `plan/features/` for dependency-invalidated fresh rematerialization.
2. Record the planning batch in `notes/logs/features/`.
3. Run the authoritative document-family tests for the changed planning artifacts.

## Verification

Canonical verification commands for this task:

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_feature_plan_docs.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the stricter fresh-rematerialization contract is captured in an authoritative feature plan
- the plan makes the no-reused-children rule explicit for dependency-invalidated nodes
- the governing task plan and development log reference each other
- the documented verification commands are run and their results are recorded honestly
