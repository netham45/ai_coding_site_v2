# Phase F10-S1: Top-Level Workflow Creation Commands

## Goal

Implement prompt-driven creation commands such as `ai-tool workflow start --kind <type> --prompt <prompt>` and equivalent node-creation entrypoints.

## Rationale

- Rationale: The system needs a real entrypoint for turning a user prompt into an initial node, workflow, and optional run under daemon control.
- Reason for existence: This phase exists so starting work is an explicit, durable command family rather than a manual setup procedure hidden behind the scenes.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`: F10 is the parent feature for this command family.
- `plan/features/02_F01_configurable_node_hierarchy.md`: F01 determines which top-level kinds may be created.
- `plan/features/07_F03_immutable_workflow_compilation.md`: F03 compiles the initial workflow after creation.
- `plan/features/13_F09_node_run_orchestration.md`: F09 optionally starts execution immediately after creation.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`
- `notes/scenarios/journeys/common_user_journeys_analysis.md`

## Scope

- Database: persist prompt-driven request inputs, initial node version, initial compiled workflow binding, and start metadata.
- CLI: implement top-level create/start commands for arbitrary supported node kinds.
- Daemon: resolve the requested kind, create the top-level node version, compile it, and optionally start the run.
- YAML: ensure node definitions are discoverable for prompt-driven top-level creation.
- Prompts: bind the incoming user prompt to initial node creation and main prompt context correctly.
- Tests: exhaustively cover valid create flows, bad kinds, missing prompt cases, compile failures on create, and create-without-run versus create-and-run behavior.
- Performance: benchmark create/start latency, especially compile-on-create overhead.
- Notes: keep getting-started and top-level creation notes aligned with the real command surface.
