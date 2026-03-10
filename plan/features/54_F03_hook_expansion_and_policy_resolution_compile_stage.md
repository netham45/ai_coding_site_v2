# Phase F03-S5: Hook Expansion And Policy Resolution Compile Stage

## Goal

Implement hook expansion and policy resolution as explicit compile stages.

## Rationale

- Rationale: Hook expansion and policy folding are some of the highest-risk compile transformations because they can reshape executable workflow structure.
- Reason for existence: This phase exists to contain those transformations in a named stage with explicit diagnostics, ordering rules, and test scope.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`: F03 is the parent compiler feature for this stage.
- `plan/features/27_F26_hook_system.md`: F26 defines the hook behavior expanded here.
- `plan/features/09_F35_project_policy_extensibility.md`: F35 defines project policy behavior folded in at this stage.
- `plan/features/53_F03_override_resolution_compile_stage.md`: F03-S4 produces the resolved documents this stage consumes.
- `plan/features/55_F03_rendering_and_compiled_payload_freeze_stage.md`: F03-S6 follows after policy and hook structure is settled.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/contracts/yaml/hook_expansion_algorithm.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/pseudocode/00_compilation_plan.md`
- `notes/pseudocode/modules/compile_workflow.md`

## Scope

- Database: persist hook-selection and policy-resolution diagnostics where needed.
- CLI: inspect hook expansion and effective policy in compile output.
- Daemon: run policy folding and deterministic hook expansion before final workflow assembly.
- YAML: support hook and policy definitions with explicit applicability and ordering semantics.
- Prompts: ensure prompt-bearing hooks resolve safely.
- Tests: exhaustively cover hook applicability, ordering, policy fold-in, and expansion rejection.
- Performance: benchmark compile overhead from hook and policy processing.
- Notes: update hook/policy notes when implementation freezes stage ordering.
