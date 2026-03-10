# Phase F08: Dependency Graph And Admission Control

## Goal

Implement valid dependency graphs, readiness checks, and run admission enforcement.

## Rationale

- Rationale: Scheduling only makes sense if dependency edges, readiness rules, and impossible waits are modeled explicitly instead of inferred ad hoc.
- Reason for existence: This phase exists to prevent blocked or invalid nodes from entering execution and to make dependency-driven waiting debuggable.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`: F01 defines the nodes and structural constraints dependencies attach to.
- `plan/features/05_F02_node_versioning_and_supersession.md`: F02 affects how dependency state behaves across regenerated versions.
- `plan/features/04_F07_durable_node_lifecycle_state.md`: F07 provides the lifecycle and wait states admission control reads.
- `plan/features/20_F15_child_node_spawning.md`: F15 creates the child nodes and edges the scheduler later admits.
- `plan/features/13_F09_node_run_orchestration.md`: F09 invokes admission and wait logic at run time.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/contracts/runtime/invalid_dependency_graph_handling.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/pseudocode/modules/check_node_dependency_readiness.md`

## Scope

- Database: dependency edges, dependency state, blocker read models.
- CLI: blockers, dependency status, and invalid-graph diagnostics.
- Daemon: dependency legality, readiness, impossible-wait detection, and admission.
- YAML: declarative dependency support in layouts and workflows.
- Prompts: blocked-state and startup-context prompts must reflect dependency truth.
- Tests: exhaustive valid/invalid graph, blocked, impossible-wait, and concurrency coverage.
- Performance: benchmark readiness classification and blocker queries.
- Notes: clarify dependency/child-summary startup context if implementation needs more explicit rules.
