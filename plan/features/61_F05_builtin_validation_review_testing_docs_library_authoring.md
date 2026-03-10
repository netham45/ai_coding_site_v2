# Phase F05B: Built-In Validation, Review, Testing, And Docs Library Authoring

## Goal

Author the built-in YAML families that define default quality-gate and documentation behavior.

## Rationale

- Rationale: Default quality-gate and documentation behavior should ship as authored assets, not as implied examples waiting for a project to fill them in.
- Reason for existence: This phase exists to provide the built-in validation, review, testing, and docs definitions the default workflow surface depends on.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/08_F05_default_yaml_library.md`: F05 is the parent feature for built-in YAML authoring.
- `plan/features/25_F21_validation_framework.md`: F21 consumes validation definitions authored here.
- `plan/features/26_F22_review_framework.md`: F22 consumes review definitions authored here.
- `plan/features/28_F23_testing_framework_integration.md`: F23 consumes testing definitions authored here.
- `plan/features/33_F29_documentation_generation.md`: F29 consumes documentation definitions authored here.
- `plan/features/60_F05_builtin_node_task_layout_library_authoring.md`: F05A covers the structural built-ins these definitions attach to.
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`: F05C covers adjacent built-ins for policy, hooks, and prompts.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/default_yaml_library_plan.md`
- `notes/planning/expansion/review_testing_docs_yaml_plan.md`
- `notes/catalogs/audit/yaml_builtins_checklist.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`

## Scope

- Database: persist built-in identity and result lineage metadata where needed.
- CLI: expose commands to inspect built-in quality-gate and docs definitions.
- Daemon: load quality-gate built-ins deterministically and enforce required gate ordering.
- YAML: author built-in validation, review, testing, and docs definitions, including failure handling and escalation references.
- Prompts: bind each quality-gate and docs built-in to its authored prompt templates and result contracts.
- Tests: exhaustively test schema validity, compileability, gate ordering, prompt bindings, and every expected success/failure contract.
- Performance: benchmark load and compile cost for the quality-gate YAML families.
- Notes: keep quality-gate/docs planning notes synchronized with the authored built-ins.

## Exit Criteria

- the default quality-gate YAML pack is complete, deterministic, and fully test-backed.
