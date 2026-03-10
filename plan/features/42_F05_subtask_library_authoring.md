# Phase F05-S1: Subtask Library Authoring

## Goal

Author the full reusable built-in subtask library and make its packaging choice explicit.

## Rationale

- Rationale: The default system needs an actual reusable subtask catalog if built-in workflows are going to compile and dispatch consistently.
- Reason for existence: This phase exists to author the subtask layer the rest of the built-in task library depends on.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/08_F05_default_yaml_library.md`: F05 is the parent feature for built-in YAML authoring.
- `plan/features/60_F05_builtin_node_task_layout_library_authoring.md`: F05A packages the structural built-ins that consume the subtask library.
- `plan/features/43_F05_prompt_pack_authoring.md`: F05-S2 provides prompts many subtasks bind to.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/default_yaml_library_plan.md`
- `notes/catalogs/inventory/yaml_inventory_v2.md`
- `notes/catalogs/audit/yaml_builtins_checklist.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`

## Scope

- Database: no major new structures beyond lineage and compile persistence.
- CLI: expose subtask-chain inspection clearly enough to validate authored subtasks.
- Daemon: compile and dispatch every built-in subtask type deterministically.
- YAML: author every required built-in subtask definition or explicitly freeze the inline-template strategy.
- Prompts: ensure subtask prompt-bearing fields are bound to the prompt pack and rendering model.
- Tests: exhaustively cover every built-in subtask definition for schema validity, compileability, dispatchability, and handler compatibility.
- Performance: benchmark dispatch and compile cost across the authored subtask catalog.
- Notes: update the YAML built-ins checklist and any subtask packaging notes as the choice is finalized.
