# Phase F01: Configurable Node Hierarchy

## Goal

Support configurable tiers and node kinds instead of hardcoding one ladder.

## Rationale

- Rationale: The specs explicitly reject a hardcoded `epic -> phase -> plan -> task` ladder, so hierarchy semantics need to be modeled as data rather than embedded assumptions.
- Reason for existence: This phase exists so projects can define their own node kinds and parent/child constraints without forking the runtime or breaking the rest of the planning model.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/03_F04_yaml_schema_system.md`: F04 defines the schemas that express configurable kinds and tiers.
- `plan/features/20_F15_child_node_spawning.md`: F15 materializes hierarchy definitions into real child nodes.
- `plan/features/21_F16_manual_tree_construction.md`: F16 covers the manual variant of tree structure on top of the same hierarchy model.
- `plan/features/09_F35_project_policy_extensibility.md`: F35 extends hierarchy behavior for project-specific ladders and policies.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/catalogs/inventory/yaml_inventory_v2.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`

## Scope

- Database: flexible node kind/tier storage and parent/child constraint storage.
- CLI: visible kind/tier reporting and top-level create-from-prompt surfaces for arbitrary `--kind`.
- Daemon: enforce parent/child legality and create top-level nodes from prompt-driven requests.
- YAML: node definition schemas and built-in/default node definitions.
- Prompts: generic node-kind placeholders and top-level creation prompt support.
- Tests: exhaustive coverage for valid/invalid hierarchies, arbitrary top-level create flows, and custom ladders.
- Performance: benchmark hierarchy traversal and create-from-prompt overhead.
- Notes: update hierarchy and entrypoint notes if custom ladders need more fields.
