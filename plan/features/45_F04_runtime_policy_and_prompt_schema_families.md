# Phase F04-S3: Runtime Policy And Prompt Schema Families

## Goal

Make runtime policy and prompt-linked YAML families explicit and rigid.

## Rationale

- Rationale: Runtime policy and prompt-linked resources shape execution behavior directly, so their contracts need schema-level validation as well.
- Reason for existence: This phase exists to freeze the allowed structure for policy documents, prompt references, and placeholder metadata before more runtime logic accumulates.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/03_F04_yaml_schema_system.md`: F04 is the parent schema feature for these runtime-facing families.
- `plan/features/09_F35_project_policy_extensibility.md`: F35 depends on policy schemas being explicit and safe.
- `plan/features/27_F26_hook_system.md`: F26 uses these schema families for hook and policy definitions.
- `plan/features/43_F05_prompt_pack_authoring.md`: F05-S2 relies on explicit prompt-linked schema rules.
- `plan/features/41_F03_variable_substitution_and_context_rendering.md`: F03-S1 depends on variable/render metadata being defined clearly.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/contracts/runtime/runtime_environment_policy_note.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/catalogs/inventory/yaml_inventory_v2.md`

## Scope

- Database: persist enough schema/resource metadata for auditability.
- CLI: inspect runtime-policy and prompt-linked YAML sources and validation results.
- Daemon: enforce validation before runtime policy or prompt references are accepted.
- YAML: author explicit schemas for:
  - runtime/session policy definitions
  - prompt-linked references and placeholders
  - variable/render metadata where applicable
- Prompts: freeze prompt placeholder and metadata rules at schema level.
- Tests: exhaustively cover allowed/illegal policy fields, placeholder declarations, and prompt-link constraints.
- Performance: benchmark policy and prompt-schema validation cost.
- Notes: update runtime-policy and prompt-library notes when the schema model is finalized.
