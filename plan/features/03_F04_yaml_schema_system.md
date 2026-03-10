# Phase F04: YAML Schema System

## Goal

Make every YAML family explicit, validated, and testable.

## Rationale

- Rationale: YAML is a first-class implementation surface in this repository, which means every family has to be explicit, validated, and auditable instead of implied by runtime code.
- Reason for existence: This phase exists to turn loose YAML conventions into enforceable contracts before compilation, execution, or review logic depends on them.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`: F01 provides the hierarchy structures the schema system must encode.
- `plan/features/44_F04_validation_review_testing_docs_rectification_schema_families.md`: F04-S2 expands schema coverage into verification, docs, and rectification families.
- `plan/features/45_F04_runtime_policy_and_prompt_schema_families.md`: F04-S3 covers runtime policy and prompt-linked schema families.
- `plan/features/08_F05_default_yaml_library.md`: F05 depends on these schemas to author valid built-in YAML assets.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/catalogs/inventory/yaml_inventory_v2.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/planning/expansion/review_testing_docs_yaml_plan.md`

## Scope

- Database: persist schema-validation metadata where auditability requires it.
- CLI: YAML validate/show commands.
- Daemon: strict schema validation before compilation or mutation.
- YAML: author schemas for node, task, subtask, layout, validation, review, testing, docs, rectification, policy, and prompt-linked families.
- Prompts: validate prompt-family metadata and placeholder requirements.
- Tests: exhaustive valid/invalid cases for every schema family.
- Performance: benchmark validation over representative YAML sets.
- Notes: update schema notes when implementation exposes new families or constraints.
