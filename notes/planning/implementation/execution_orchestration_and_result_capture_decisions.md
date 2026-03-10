# Execution Orchestration And Result Capture Decisions

## Summary

Feature `66_F05_execution_orchestration_and_result_capture` adds an explicit execution-result contract to subtask attempts and exposes durable attempt-history reads without moving real shell or tool execution into the daemon.

## Decisions

- Add `subtask_attempts.execution_result_json` as the canonical explicit result payload for session-reported command or tool outcomes.
- Keep `subtask_attempts.output_json` for compatibility because validation, review, testing, heartbeat, and history flows already read from it.
- Mirror `execution_result_json` into `output_json` on `subtask complete` and `subtask fail` so existing runtime consumers continue to work while newer code can read the explicit field.
- Expose durable attempt history through daemon and CLI reads:
  - `GET /api/nodes/{node_id}/subtask-attempts`
  - `GET /api/subtask-attempts/{attempt_id}`
  - `ai-tool subtask attempts --node <id>`
  - `ai-tool subtask attempt-show --attempt <id>`
- Add `--result-file <path>` to `subtask complete` and `subtask fail` so the CLI can send structured execution-result payloads without forcing large JSON bodies onto the shell command line.

## Why This Slice Is Bounded

- The daemon still does not own real shell or tool execution for ordinary subtasks.
- Session-backed execution remains the live path.
- This phase makes the result contract explicit, durable, and inspectable so later execution-oriented features can build on stable history instead of ad hoc prompt text.

## Database

- Added `subtask_attempts.execution_result_json`.
- Added an index supporting repeated attempt-history reads by run and subtask creation order.

## CLI And Daemon

- Completion and failure mutations now accept explicit execution-result payloads.
- Operators and AI sessions can inspect prior attempts without relying only on `subtask current`.

## Remaining Boundary

- Real daemon-owned external tool execution remains deferred.
- Environment launch metadata and execution-result payloads are separate dimensions:
  - `execution_environment_json` describes where work ran
  - `execution_result_json` describes what that work returned
