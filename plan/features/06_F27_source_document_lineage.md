# Phase F27: Source Document Lineage

## Goal

Track every source YAML and related compile input used to create historical workflows.

## Rationale

- Rationale: Compiled workflows must be explainable back to their exact source YAML, overrides, prompts, and hashes if the system is going to be reproducible.
- Reason for existence: This phase exists so a historical workflow can always answer which source documents created it rather than leaving compilation inputs implicit.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/10_F06_override_and_merge_resolution.md`: F06 produces part of the resolved source chain that lineage must preserve.
- `plan/features/07_F03_immutable_workflow_compilation.md`: F03 records the source inputs that led to compiled workflows.
- `plan/features/35_F36_auditable_history_and_reproducibility.md`: F36 depends on source lineage for reconstruction and audit.
- `plan/features/56_F03_compiled_workflow_persistence_and_failure_diagnostics.md`: F03-S7 persists the lineage-bearing compiled artifacts.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/catalogs/vocabulary/state_value_catalog.md`
- `notes/pseudocode/catalog/source_to_artifact_map.md`

## Scope

- Database: source docs, hashes, roles, and compile-input lineage.
- CLI: source and resolved YAML lineage inspection.
- Daemon: capture lineage during compile/recompile.
- YAML: make all compile-relevant inputs addressable and hashable.
- Prompts: bind prompt-template identity to source lineage where applicable.
- Tests: exhaustive lineage capture, hashing, and historical resolution tests.
- Performance: benchmark lineage persistence and lookup paths.
- Notes: update source-role taxonomy if missing categories appear.
