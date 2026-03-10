# Phase F10-S2: Stage Context Retrieval And Startup Context Assembly

## Goal

Assemble and expose the exact stage context an active session needs at stage start.

## Rationale

- Rationale: An AI session can only behave deterministically if the stage prompt and surrounding context are assembled from durable state in a repeatable way.
- Reason for existence: This phase exists to define exactly what startup context the CLI exposes and where that context comes from.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`: F10 is the parent feature for this retrieval surface.
- `plan/features/13_F09_node_run_orchestration.md`: F09 supplies the current stage and durable context sources.
- `plan/features/11_F08_dependency_graph_and_admission_control.md`: F08 contributes dependency summaries and blocker context.
- `plan/features/31_F28_prompt_history_and_summary_history.md`: F28 contributes prior prompt and summary context for stage startup.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/scenarios/journeys/common_user_journeys_analysis.md`

## Scope

- Database: persist or derive prompt/context inputs, dependency summaries, child summaries, prior summaries, and relevant result references.
- CLI: implement reliable `current`, `prompt`, and `context` retrieval surfaces with structured output.
- Daemon: build authoritative stage-start context from durable state rather than terminal history.
- YAML: declaratively identify which context categories a task/subtask expects where needed.
- Prompts: make prompt payloads explicitly reference dependency summaries, child summaries, and prior relevant results.
- Tests: exhaustively cover startup context composition, missing-context cases, dependency summary injection, and child-summary visibility.
- Performance: benchmark repeated context assembly and retrieval for hot stages.
- Notes: clarify stage-start context rules in runtime and journey notes if implementation reveals missing categories.
