# AI-Facing CLI Command Loop Decisions

## Scope

This note records the implementation decisions for `plan/features/14_F10_ai_facing_cli_command_loop.md`.

## Decisions

- the AI-facing retrieval commands are now daemon-backed end to end: `session bind`, `session show-current`, `workflow current`, `subtask current`, `subtask prompt`, and `subtask context`
- the AI-facing progress commands are now daemon-backed end to end: `subtask start`, `subtask heartbeat`, `subtask complete`, `subtask fail`, `workflow advance`, `workflow pause`, and `workflow resume`
- `subtask prompt` returns the compiled prompt payload frozen on the current compiled subtask, rather than re-rendering from mutable YAML at read time
- `subtask context` returns the durable current-attempt context if an attempt exists, otherwise it returns the synthesized current subtask input snapshot
- `subtask heartbeat` is currently persisted by updating the active attempt payload and run cursor metadata with `last_heartbeat_at`; dedicated heartbeat history remains a later phase
- `summary register` is currently staged by attaching registered summary metadata and content to the active subtask attempt payload; dedicated summary-history tables remain a later phase

## Deferred work

- dedicated summary tables and summary-history CLI
- dedicated heartbeat history and idle-event history
- session-binding ownership tied to durable `node_runs`
- richer prompt/context retrieval that includes prior summaries, artifacts, and validation history
- run-scoped and attempt-scoped summary inspection commands

## Notes impact

- runtime notes now describe the real read-side and mutation-side command loop available to active AI sessions
- CLI notes now reflect the daemon-backed prompt/context and workflow pause/resume commands
- prompt notes now explicitly warn that heartbeat and summary registration are staged durable surfaces ahead of the fuller history phases
