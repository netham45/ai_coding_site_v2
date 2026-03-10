# Phase F03-S1: Variable Substitution And Context Rendering

## Goal

Support invoker-driven variable substitution in YAML and prompt/command rendering, including forms such as `{{variable}}`.

## Rationale

- Rationale: Prompt assets and YAML definitions need parameterization, but rendering has to be deterministic about scope, timing, and auditability.
- Reason for existence: This phase exists to define where substitution happens and to keep late-bound values from undermining compiled workflow stability.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`: F03 is the parent feature for compile-time rendering and freeze semantics.
- `plan/features/43_F05_prompt_pack_authoring.md`: F05-S2 authors prompt assets that rely on this rendering model.
- `plan/features/55_F03_rendering_and_compiled_payload_freeze_stage.md`: F03-S6 is the later compiler slice that freezes rendered payloads.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/catalogs/inventory/yaml_inventory_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/pseudocode/00_compilation_plan.md`

## Scope

- Database: persist rendered-versus-source values where auditability requires it, especially for prompts and commands.
- CLI: expose enough source/rendered context to debug substitution results safely.
- Daemon: implement the rendering engine, variable precedence rules, missing-variable behavior, escaping, and safe render timing.
- YAML: add explicit schema support for invoker variables, renderable fields, and variable scope inheritance.
- Prompts: allow prompt assets and subtask fields to reference rendered variables deterministically.
- Tests: exhaustively cover substitution success, missing variables, shadowing, escaping, nested scopes, invoker inheritance, and illegal render targets.
- Performance: benchmark render cost during compile and stage startup.
- Notes: update schema, prompt, and code-vs-YAML notes to freeze rendering semantics.
