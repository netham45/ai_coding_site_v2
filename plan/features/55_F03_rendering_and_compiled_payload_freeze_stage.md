# Phase F03-S6: Rendering And Compiled Payload Freeze Stage

## Goal

Render variables/placeholders and freeze prompt/command payloads into compiled artifacts.

## Rationale

- Rationale: Prompt payloads, commands, and arguments need their variables resolved at a deliberate boundary so runtime execution sees stable artifacts.
- Reason for existence: This phase exists to freeze rendered payloads into compiled outputs instead of letting late rendering create ambiguity during execution or audit.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`: F03 is the parent compiler feature for this stage.
- `plan/features/41_F03_variable_substitution_and_context_rendering.md`: F03-S1 defines the substitution semantics this stage must honor.
- `plan/features/43_F05_prompt_pack_authoring.md`: F05-S2 authors many of the prompt payloads frozen here.
- `plan/features/54_F03_hook_expansion_and_policy_resolution_compile_stage.md`: F03-S5 determines the final structure before rendering occurs.
- `plan/features/56_F03_compiled_workflow_persistence_and_failure_diagnostics.md`: F03-S7 persists the rendered and frozen artifacts.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/pseudocode/00_compilation_plan.md`
- `notes/pseudocode/modules/compile_workflow.md`

## Scope

- Database: persist rendered versus source payloads where auditability requires it.
- CLI: expose rendered compile outputs for inspection/debugging.
- Daemon: render prompts, commands, args, env, and related payload fields during compile or stage-assembly at the correct boundary.
- YAML: mark or define renderable fields and substitution rules.
- Prompts: freeze rendered prompt payloads and placeholder bindings deterministically.
- Tests: exhaustively cover render timing, placeholder substitution, missing data, and frozen payload reproducibility.
- Performance: benchmark rendering overhead during compile and stage assembly.
- Notes: update rendering and prompt notes when semantics are frozen.
