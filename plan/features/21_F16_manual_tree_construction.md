# Phase F16: Manual Tree Construction

## Goal

Let users define and edit trees manually without breaking layout-driven safety.

## Rationale

- Rationale: The system cannot assume every hierarchy comes from automatic decomposition; operators need a supported path for hand-built structures too.
- Reason for existence: This phase exists to let manual structure coexist with layout-driven automation without creating authority conflicts or unsafe rewrites.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`: F01 supplies the same hierarchy rules manual construction must respect.
- `plan/features/20_F15_child_node_spawning.md`: F15 is the automatic construction path manual editing has to coexist with.
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`: F19 has to preserve or reinterpret manual structure during rebuilds.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/contracts/parent_child/manual_vs_auto_tree_interaction.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/pseudocode/state_machines/parent_child_authority.md`

## Scope

- Database: structural authority metadata and origin tracking.
- CLI: manual create/edit/replace flows for tree structure.
- Daemon: hybrid-tree safety and reconciliation enforcement.
- YAML: manual-layout and hybrid-authority support where needed.
- Prompts: minimal manual-reconciliation guidance prompts.
- Tests: exhaustive manual-only, hybrid, authority-conflict, and regeneration-after-manual-edit coverage.
- Performance: benchmark tree inspection with authority metadata.
- Notes: update manual-vs-auto notes when real edge cases appear.
