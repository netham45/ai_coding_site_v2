# Phase F10-S3: AI CLI Bootstrap And Work Retrieval Commands

## Goal

Implement the AI-facing CLI command family for discovering current work.

## Rationale

- Rationale: The command loop has to start with safe read-side commands that tell a session what it is bound to and what work is current.
- Reason for existence: This phase exists to provide the minimum authoritative retrieval surface an AI needs before it performs any progress mutation.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`: F10 is the parent feature for this command family.
- `plan/features/16_F12_session_binding_and_resume.md`: F12 determines which session these read-side commands are scoped to.
- `plan/features/38_F10_stage_context_retrieval_and_startup_context.md`: F10-S2 defines the data those commands return.
- `plan/features/47_F10_ai_cli_progress_and_stage_transition_commands.md`: F10-S4 complements these retrieval commands with the write-side mutations.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/scenarios/journeys/common_user_journeys_analysis.md`

## Scope

- Database: ensure work-retrieval state is durably queryable.
- CLI: implement:
  - `session bind`
  - `session show-current`
  - `workflow current`
  - `subtask current`
  - `subtask prompt`
  - `subtask context`
- Daemon: validate retrieval requests against authoritative run/session state.
- YAML: no new semantics beyond compiled bindings and context categories.
- Prompts: bootstrap prompts must match the actual retrieval commands.
- Tests: exhaustively cover missing-run, wrong-session, stale-session, and valid retrieval behavior.
- Performance: benchmark hot prompt/context retrieval latency.
- Notes: update CLI/runtime notes if retrieval response shapes evolve.
