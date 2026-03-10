# Phase F05: Default YAML Library

## Goal

Author the built-in YAML library needed for the default system to run end to end.

## Rationale

- Rationale: A schema inventory is not enough to run the system; the default product also needs concrete authored YAML assets that satisfy those schemas.
- Reason for existence: This phase exists to supply the built-in definitions the rest of the runtime, CLI, and prompt model assume are present out of the box.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/03_F04_yaml_schema_system.md`: F04 defines the schema contracts every built-in asset must satisfy.
- `plan/features/42_F05_subtask_library_authoring.md`: F05-S1 authors reusable subtask library details.
- `plan/features/43_F05_prompt_pack_authoring.md`: F05-S2 provides the prompt assets built-ins bind to.
- `plan/features/60_F05_builtin_node_task_layout_library_authoring.md`: F05A covers the structural built-in YAML families.
- `plan/features/61_F05_builtin_validation_review_testing_docs_library_authoring.md`: F05B covers the quality-gate and docs built-ins.
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`: F05C covers runtime policy, hooks, and prompt library built-ins.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/inventory/default_yaml_library_plan.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/catalogs/audit/yaml_builtins_checklist.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`

## Scope

- Database: support built-in loading and lineage only.
- CLI: inspect built-ins versus project overrides.
- Daemon: deterministic built-in loading.
- YAML: author node/task/subtask/layout/validation/review/testing/docs/rectification/policy files from the checklist.
- Prompts: bind built-in YAML tasks to built-in prompt assets.
- Tests: exhaustive schema-validity and compileability tests for every built-in file.
- Performance: benchmark built-in load and compile startup cost.
- Notes: keep the YAML built-ins checklist synchronized with authored files.
