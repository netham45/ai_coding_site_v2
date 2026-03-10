# Phase F18: Child Merge And Reconcile Pipeline

## Goal

Merge child finals deterministically and reconcile parent output safely.

## Rationale

- Rationale: Child execution only becomes useful when parent state can absorb child outputs in a deterministic and reviewable way.
- Reason for existence: This phase exists to define how child finals merge back into the parent and how the parent re-establishes its own coherent output afterward.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/20_F15_child_node_spawning.md`: F15 produces the child outputs this pipeline merges.
- `plan/features/12_F17_deterministic_branch_model.md`: F17 defines the branch and commit anchors merge ordering relies on.
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`: F19 rebuilds and reconcile work interact heavily with this pipeline.
- `plan/features/22_F20_conflict_detection_and_resolution.md`: F20 handles blocked merge cases discovered here.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/pseudocode/modules/collect_child_results.md`

## Scope

- Database: merge ordering, reconcile results, post-merge stage results.
- CLI: merge order, child finals, and reconcile inspection.
- Daemon: deterministic merge execution and parent-local reconcile flow.
- YAML: reconcile task definitions and merge-related subtasks.
- Prompts: parent-local reconcile prompts.
- Tests: exhaustive ordering, reconcile no-op/change, and failed reconcile coverage.
- Performance: benchmark repeated merge/reconcile runs.
- Notes: update merge/reconcile notes if ordering fields expand.
