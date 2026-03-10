# Phase F04-S2: Verification, Docs, And Rectification Schema Families

## Goal

Author rigid schema families for the higher-order YAML artifacts instead of treating them as loosely implied extensions.

## Rationale

- Rationale: Higher-order YAML artifacts such as validation, review, testing, docs, and rectification definitions are too important to remain loosely specified.
- Reason for existence: This phase exists to give those families the same rigid schema treatment as the core structural YAML surface.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/03_F04_yaml_schema_system.md`: F04 is the parent schema feature for this higher-order family expansion.
- `plan/features/25_F21_validation_framework.md`: F21 consumes validation schema families.
- `plan/features/26_F22_review_framework.md`: F22 consumes review schema families.
- `plan/features/28_F23_testing_framework_integration.md`: F23 consumes testing schema families.
- `plan/features/33_F29_documentation_generation.md`: F29 consumes documentation schema families.
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`: F19 consumes rectification schema families.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/planning/expansion/review_testing_docs_yaml_plan.md`
- `notes/catalogs/inventory/yaml_inventory_v2.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`

## Scope

- Database: persist schema-family and validation metadata where auditability requires it.
- CLI: expose schema validation and schema-family inspection for these families.
- Daemon: enforce schema validation before compilation or runtime use.
- YAML: author explicit rigid schemas for:
  - validation definitions
  - review definitions
  - testing definitions
  - documentation definitions
  - rectification definitions
- Prompts: validate schema-level prompt-bearing fields and prompt references in these families.
- Tests: exhaustively cover valid/invalid examples for every field and every family.
- Performance: benchmark validation cost across large definition packs.
- Notes: update schema and family-inventory notes when implementation freezes the exact field sets.
