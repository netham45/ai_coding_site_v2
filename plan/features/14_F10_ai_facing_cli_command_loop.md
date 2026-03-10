# Phase F10: AI-Facing CLI Command Loop

## Goal

Implement the CLI loop used by active AI sessions.

## Rationale

- Rationale: AI sessions need a real operational interface for reading context, reporting progress, and advancing work without bypassing durable state.
- Reason for existence: This phase exists to make the session-facing command loop an explicit contract that matches runtime behavior and prompt guidance.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`: F09 is the authoritative runtime surface this CLI loop drives.
- `plan/features/15_F11_operator_cli_and_introspection.md`: F11 is the complementary operator-facing inspection surface.
- `plan/features/37_F10_top_level_workflow_creation_commands.md`: F10-S1 covers workflow creation entrypoints.
- `plan/features/38_F10_stage_context_retrieval_and_startup_context.md`: F10-S2 covers stage context retrieval.
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`: F10-S3 covers AI bootstrap and work retrieval commands.
- `plan/features/47_F10_ai_cli_progress_and_stage_transition_commands.md`: F10-S4 covers mutation and transition commands.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/scenarios/journeys/common_user_journeys_analysis.md`

## Scope

- Database: ensure prompt/context/progress state is durably queryable.
- CLI: implement prompt/context retrieval, start, heartbeat, complete, fail, summary, and workflow control commands.
- Daemon: validate CLI mutations through authoritative runtime logic.
- YAML: use compiled task/subtask bindings only.
- Prompts: bootstrap, correction, missed-step, and stage-guidance prompts must align with real CLI commands.
- Tests: exhaustive command-level success, malformed input, and race-sensitive coverage.
- Performance: benchmark prompt/context retrieval and progress-command latency.
- Notes: update CLI/runtime docs if command shapes diverge.
