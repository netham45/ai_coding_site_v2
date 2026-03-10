# Phase F03-S3: Schema Validation Compile Stage

## Goal

Implement schema validation as a dedicated compile stage with durable diagnostics.

## Rationale

- Rationale: Schema rejection needs to happen before merge and expansion so invalid sources fail with precise diagnostics at the right boundary.
- Reason for existence: This phase exists to isolate schema validation as its own compile stage instead of burying those failures deeper in the pipeline.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`: F03 is the parent compiler feature for this stage.
- `plan/features/03_F04_yaml_schema_system.md`: F04 provides the schemas applied during validation.
- `plan/features/51_F03_source_discovery_and_loading_pipeline.md`: F03-S2 feeds source documents into this stage.
- `plan/features/53_F03_override_resolution_compile_stage.md`: F03-S4 runs after schema-valid sources pass this gate.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/catalogs/inventory/yaml_inventory_v2.md`
- `notes/contracts/persistence/compile_failure_persistence.md`
- `notes/pseudocode/00_compilation_plan.md`
- `notes/pseudocode/modules/compile_workflow.md`

## Scope

- Database: persist schema-validation failures and stage diagnostics.
- CLI: inspect schema-validation failures distinctly from later compile failures.
- Daemon: run schema validation after source load and before merge/expansion.
- YAML: validate every relevant family through the canonical schemas.
- Prompts: validate prompt-linked metadata at compile time.
- Tests: exhaustively cover schema-stage rejection across all major families.
- Performance: benchmark compile-time validation overhead.
- Notes: update compile-failure notes if schema-stage failure classes need refinement.
