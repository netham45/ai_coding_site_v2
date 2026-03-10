# Phase F26: Hook System

## Goal

Support policy-driven hook insertion across lifecycle points.

## Rationale

- Rationale: Cross-cutting lifecycle behavior needs a reusable insertion mechanism so policy can alter workflows without duplicating task definitions everywhere.
- Reason for existence: This phase exists to give the compiler and runtime a disciplined hook model rather than letting special cases spread through feature code.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/03_F04_yaml_schema_system.md`: F04 defines the hook schema families and legal structure.
- `plan/features/09_F35_project_policy_extensibility.md`: F35 uses hooks as a major extensibility mechanism.
- `plan/features/07_F03_immutable_workflow_compilation.md`: F03 expands hooks into compiled workflow structure.
- `plan/features/54_F03_hook_expansion_and_policy_resolution_compile_stage.md`: F03-S5 is the concrete hook expansion stage.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/contracts/yaml/hook_expansion_algorithm.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/pseudocode/00_compilation_plan.md`

## Scope

- Database: persist selected/expanded hooks and hook lineage where needed.
- CLI: hooks-in-effect and hook-origin inspection.
- Daemon: hook selection, ordering, expansion, and legality checks.
- YAML: hook schemas and built-in hook definitions.
- Prompts: load and compile prompt-bearing hooks safely.
- Tests: exhaustive applicability, ordering, conflict, and expansion-diagnostic coverage.
- Performance: benchmark compile overhead from hook expansion.
- Notes: update hook algorithm notes if ordering edge cases emerge.
