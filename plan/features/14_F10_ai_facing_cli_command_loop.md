# Phase F10: AI-Facing CLI Command Loop

## Goal

Implement the CLI loop used by active AI sessions.

## Scope

- Database: ensure prompt/context/progress state is durably queryable.
- CLI: implement prompt/context retrieval, start, heartbeat, complete, fail, summary, and workflow control commands.
- Daemon: validate CLI mutations through authoritative runtime logic.
- YAML: use compiled task/subtask bindings only.
- Prompts: bootstrap, correction, missed-step, and stage-guidance prompts must align with real CLI commands.
- Tests: exhaustive command-level success, malformed input, and race-sensitive coverage.
- Performance: benchmark prompt/context retrieval and progress-command latency.
- Notes: update CLI/runtime docs if command shapes diverge.
