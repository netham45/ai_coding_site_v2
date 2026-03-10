# Phase F05-S2: Prompt Pack Authoring

## Goal

Author the full built-in prompt pack as implementation assets rather than placeholders.

## Rationale

- Rationale: Prompt behavior is a first-class asset in this architecture, so the default system needs real authored prompts instead of placeholder strings.
- Reason for existence: This phase exists to ship the concrete prompt pack that execution, recovery, review, testing, and docs stages consume.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/08_F05_default_yaml_library.md`: F05 is the parent feature for built-in assets.
- `plan/features/42_F05_subtask_library_authoring.md`: F05-S1 authors prompt-bearing subtask definitions.
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`: F05C packages the runtime-policy, hook, and prompt library built-ins.
- `plan/features/41_F03_variable_substitution_and_context_rendering.md`: F03-S1 defines how prompt placeholders render.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/prompts/prompt_library_plan.md`
- `notes/catalogs/inventory/default_yaml_library_plan.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/planning/expansion/review_testing_docs_yaml_plan.md`
- `notes/scenarios/journeys/common_user_journeys_analysis.md`

## Scope

- Database: ensure prompt-template identity and prompt history can reference authored assets cleanly.
- CLI: expose prompt inspection against real authored prompt files.
- Daemon: load, render, and issue authored prompt assets reliably.
- YAML: bind built-in tasks/subtasks/reviews/testing/docs/runtime behaviors to concrete prompt assets.
- Prompts: author the full prompt pack, including decomposition, execution, recovery, missed-step, pause, review, testing, docs, and child-session prompts.
- Tests: exhaustively validate prompt asset loading, placeholder coverage, rendering compatibility, and prompt-to-stage contract alignment.
- Performance: benchmark prompt-pack load and render costs.
- Notes: keep prompt library notes synchronized with actual authored assets.
