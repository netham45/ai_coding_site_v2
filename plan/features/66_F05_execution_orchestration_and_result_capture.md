# Phase F05-S1: Execution Orchestration And Result Capture

## Goal

Extend the durable command loop to capture richer execution results and, where intended, support real tool-execution orchestration semantics.

## Rationale

- Rationale: The current runtime owns prompts, context, heartbeats, summaries, and advancement well, but Flow 05 still stops short of a richer execution-result contract for tool invocations and environment-mediated command execution.
- Reason for existence: This phase exists to decide and implement how much actual execution semantics belong in the node-run flow instead of leaving them implied by prompt text.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`: F09 introduced durable run and subtask attempt orchestration.
- `plan/features/14_F10_ai_facing_cli_command_loop.md`: F10 provides the current AI-facing loop that this phase extends.
- `plan/features/36_F33_optional_isolated_runtime_environments.md`: F33 already persists environment metadata that richer execution capture may need.
- `plan/features/39_F12_tmux_session_manager.md`: F12-S1 provides the session backend used during active execution.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/contracts/runtime/runtime_environment_policy_note.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`

## Scope

- Database: persist richer execution-result payloads, command results, and any additional attempt-level execution metadata needed for reproducibility.
- CLI: expose reads and mutations for execution results without relying on hidden terminal state.
- Daemon: define and implement the real execution-result contract for commands, tool invocations, and environment-mediated steps.
- YAML: keep execution orchestration semantics code-owned; YAML may declare commands and policies, but not live execution authority.
- Prompts: align runtime prompts with the actual execution-result contract so prompts do not imply unsupported behavior.
- Tests: exhaustively cover result capture, failure paths, retry semantics, environment-linked execution metadata, and inspection reads.
- Performance: benchmark result reads and attempt updates under repeated execution-heavy loops.
- Notes: update runtime, CLI, environment, and prompt notes to match the final execution contract.
