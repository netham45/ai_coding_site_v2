# Phase F06: Override And Merge Resolution

## Goal

Implement deterministic project-local override behavior across the YAML surface.

## Rationale

- Rationale: Local overrides only remain safe if their merge behavior is deterministic, inspectable, and consistent across YAML families.
- Reason for existence: This phase exists to stop project customization from becoming order-dependent or ambiguous in ways that would break compilation and traceability.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/03_F04_yaml_schema_system.md`: F04 determines which fields and families can be overridden.
- `plan/features/06_F27_source_document_lineage.md`: F27 records the source chain before and after override fold-in.
- `plan/features/09_F35_project_policy_extensibility.md`: F35 uses override resolution as its main customization mechanism.
- `plan/features/53_F03_override_resolution_compile_stage.md`: F03-S4 is the concrete compiler slice for this feature.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/contracts/yaml/override_conflict_semantics.md`
- `notes/contracts/yaml/override_versioning_note.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/pseudocode/00_compilation_plan.md`

## Scope

- Database: override lineage and conflict records.
- CLI: override-chain and resolved-doc inspection.
- Daemon: deterministic override merge semantics.
- YAML: override schemas and field-level merge modes across families.
- Prompts: prompt override semantics with full auditability.
- Tests: exhaustive missing-target, ambiguity, conflict, and prompt-override coverage.
- Performance: benchmark large override sets and merge resolution.
- Notes: update override semantics notes if real fields require new merge rules.
