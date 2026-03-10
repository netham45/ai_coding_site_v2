# Phase F30: Code Provenance And Rationale Mapping

## Goal

Track code/entity history and rationale links back to nodes and prompts.

## Rationale

- Rationale: Documentation, auditability, and change inspection all depend on linking code entities back to node lineage and the rationale that produced them.
- Reason for existence: This phase exists to make code history explainable in orchestration terms instead of leaving changes disconnected from their planning context.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/05_F02_node_versioning_and_supersession.md`: F02 provides version lineage that code provenance links back to.
- `plan/features/15_F11_operator_cli_and_introspection.md`: F11 exposes provenance and rationale inspection surfaces.
- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`: F31 provides the durable record this mapping attaches to.
- `plan/features/33_F29_documentation_generation.md`: F29 consumes provenance and rationale to generate documentation views.
- `plan/features/35_F36_auditable_history_and_reproducibility.md`: F36 uses provenance to support later reconstruction and explanation.
- `plan/features/59_F30_database_provenance_docs_audit_schema_family.md`: F30A is the concrete schema slice supporting this feature.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/provenance/provenance_identity_strategy.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/catalogs/audit/auditability_checklist.md`
- `notes/pseudocode/modules/update_provenance_for_node.md`

## Scope

- Database: entity, relation, change, and rationale-link storage.
- CLI: entity history, changed-by, rationale, and relation inspection.
- Daemon: provenance extraction and rationale persistence at the right lifecycle points.
- YAML: provenance-policy tuning inputs where declarative control is appropriate.
- Prompts: docs/rationale prompts consume provenance; identity remains code-owned.
- Tests: exhaustive exact-match, inferred-match, rename/move, and confidence-reporting coverage.
- Performance: benchmark provenance extraction and query paths.
- Notes: update provenance identity notes if stronger matching categories are needed.
