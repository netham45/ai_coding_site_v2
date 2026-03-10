# Phase F05A: Built-In Node, Task, Subtask, And Layout Library Authoring

## Goal

Author the built-in YAML families that define the default structural workflow surface.

## Rationale

- Rationale: The default product needs a structural YAML library that defines how nodes, tasks, subtasks, and layouts fit together out of the box.
- Reason for existence: This phase exists to author the built-in structural assets the compiler and runtime assume are present for default operation.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/08_F05_default_yaml_library.md`: F05 is the parent feature for built-in YAML authoring.
- `plan/features/42_F05_subtask_library_authoring.md`: F05-S1 authors reusable subtasks consumed by the structural library.
- `plan/features/43_F05_prompt_pack_authoring.md`: F05-S2 provides the prompt bindings structural assets reference.
- `plan/features/61_F05_builtin_validation_review_testing_docs_library_authoring.md`: F05B covers adjacent built-in families that should stay consistent.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/default_yaml_library_plan.md`
- `notes/catalogs/audit/yaml_builtins_checklist.md`
- `notes/catalogs/inventory/yaml_inventory_v2.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`

## Scope

- Database: persist built-in identity and lineage metadata where needed for inspection.
- CLI: expose commands to list, inspect, and diff built-in structural YAML assets against overrides.
- Daemon: load structural built-ins deterministically and reject incomplete default packs.
- YAML: author built-in node definitions, task definitions, subtask definitions, layout definitions, and related variable-substitution-aware defaults.
- Prompts: bind each structural built-in to the correct prompt assets and placeholder contracts.
- Tests: exhaustively test schema validity, compileability, substitution behavior, and structural completeness of every built-in asset.
- Performance: benchmark built-in discovery and compilation cost for the structural library.
- Notes: keep built-in library notes synchronized with the actual authored structural assets.

## Exit Criteria

- the default structural YAML pack is complete enough to drive end-to-end workflow compilation.
