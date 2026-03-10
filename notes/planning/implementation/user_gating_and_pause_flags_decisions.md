# User Gating And Pause Flags Decisions

## Phase

- `plan/features/29_F24_user_gating_and_pause_flags.md`

## Decisions

1. User-gated pauses are now durable runtime state, not inferred operator convention. The active pause contract is stored in `node_run_state.execution_cursor_json.pause_context` and mirrored into the lifecycle row so `node pause-state` remains a cheap read path.
2. Pause history is persisted in the bounded `workflow_events` table instead of overloading `daemon_mutation_events`. The current pause event family is intentionally narrow: `pause_entered`, `pause_cleared`, and `pause_resumed`.
3. Approval and resume are separate actions. `node approve` / `workflow approve` only mark the active pause flag approved; they do not resume execution. `workflow resume` is rejected until the current non-manual pause flag has been approved.
4. Compiled subtasks now retain YAML-defined `block_on_user_flag` and optional `pause_summary_prompt` fields, so a workflow can pause before starting a gated subtask without losing the gate metadata during compilation.
5. Recovery-owned resume paths remain allowed to bypass approval checks through an explicit forced-resume branch. This keeps replacement-session and recovery behavior from deadlocking on operator-only approval semantics when the daemon is resuming a run it already owns.
6. Operator event inspection now deliberately merges authority mutations and workflow events behind `node events`, with `event_scope` distinguishing the two families. That keeps pause visibility operator-friendly without forcing every caller to understand multiple raw tables.
7. Performance guardrails for this phase focus on pause-state inspection rather than mutation throughput. The pause-state view is expected to stay in the low-subsecond range because it is part of the steady-state operator and recovery loop.
