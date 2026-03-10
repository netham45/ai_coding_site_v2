# Phase F15: Child Node Spawning

## Goal

Create and run child nodes from layouts with durable lineage and dependency-aware scheduling.

## Rationale

- Rationale: Declarative layouts are only useful if the runtime can materialize them into concrete child nodes with real lineage and scheduling state.
- Reason for existence: This phase exists to bridge decomposition intent into actual executable child work under daemon control.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`: F01 provides the hierarchy shapes layouts materialize.
- `plan/features/05_F02_node_versioning_and_supersession.md`: F02 gives spawned children durable lineage and version identity.
- `plan/features/07_F03_immutable_workflow_compilation.md`: F03 compiles child workflows after materialization.
- `plan/features/11_F08_dependency_graph_and_admission_control.md`: F08 schedules spawned children based on dependency truth.
- `plan/features/21_F16_manual_tree_construction.md`: F16 is the manual counterpart that must coexist with layout-based spawning.
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`: F18 consumes child outputs after spawning and execution.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/pseudocode/modules/materialize_layout_children.md`

## Scope

- Database: child node creation, parent-child lineage, scheduling state.
- CLI: child materialization and child-state inspection surfaces.
- Daemon: layout materialization, child creation, scheduling, and parent wait behavior.
- YAML: default layout-driven child-spawn definitions.
- Prompts: layout generation and child-creation guidance prompts.
- Tests: exhaustive idempotent materialization, duplicate protection, ready/blocked scheduling, and create-from-layout coverage.
- Performance: benchmark materialization and scheduling with larger child sets.
- Notes: update child-materialization notes if insertion-point behavior changes.
