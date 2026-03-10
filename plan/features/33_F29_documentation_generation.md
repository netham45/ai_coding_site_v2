# Phase F29: Documentation Generation

## Goal

Generate local and merged documentation views using code plus rationale/provenance data.

## Rationale

- Rationale: The notes call for generated documentation that reflects both code structure and the rationale/provenance graph behind it.
- Reason for existence: This phase exists to turn accumulated history and code analysis into usable documentation outputs rather than leaving that information fragmented.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`: F18 affects merged-document views after child reconciliation.
- `plan/features/32_F30_code_provenance_and_rationale_mapping.md`: F30 supplies the provenance and rationale information docs consume.
- `plan/features/35_F36_auditable_history_and_reproducibility.md`: F36 sets the auditability bar for generated documentation outputs.
- `plan/features/61_F05_builtin_validation_review_testing_docs_library_authoring.md`: F05B authors built-in docs-related YAML definitions.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/planning/expansion/review_testing_docs_yaml_plan.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/catalogs/audit/auditability_checklist.md`

## Scope

- Database: docs definitions, outputs, and doc history.
- CLI: docs build/list/show commands.
- Daemon: docs stage execution at the correct lifecycle points.
- YAML: documentation definition family and output policies.
- Prompts: docs-generation prompts for node and tree views.
- Tests: exhaustive local-doc, merged-doc, rebuild-doc, and docs-failure coverage.
- Performance: benchmark doc generation over representative trees.
- Notes: update docs notes if scope or ordering changes.
