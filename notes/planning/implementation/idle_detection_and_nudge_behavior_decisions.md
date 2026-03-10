# Idle Detection And Nudge Behavior Decisions

## Scope

This note records the implementation boundary for `plan/features/18_F13_idle_detection_and_nudge_behavior.md`.

## Decisions

- Idle detection is now derived from the existing session poller plus the canonical durable primary session record, not from a new heartbeat-history schema.
- No new migration was added in this slice. Idle audit is staged through `session_events`, and pause escalation remains canonical in durable run state.
- `session nudge --node <id>` now exists as a daemon-backed command that inspects the active primary session's rendered pane content, including alt-screen captures, and records durable nudge events.
- The current bounded nudge policy is runtime-configured through `AICODING_SESSION_IDLE_THRESHOLD_SECONDS` and `AICODING_SESSION_MAX_NUDGE_COUNT`.
- The final allowed nudge uses stronger repeated-missed-step prompt text before any later pause escalation.
- Once the nudge budget is exhausted, the daemon pauses the run with `pause_flag_name = "idle_nudge_limit_exceeded"` instead of nudging indefinitely.
- The daemon now runs an autonomous idle-nudge background loop that polls active primary sessions and applies the same nudge/escalation policy without requiring an external CLI trigger.
- Autonomous daemon nudging now waits for confirmed `unchanged_screen_past_idle_threshold` evidence before sending the first nudge, so the background loop does not act on `first_sample_idle_threshold_exceeded` alone.
- Once the current compiled subtask has durably registered at least one summary, further idle nudges are suppressed for that active session attempt because the task has already reached end-of-flow output production and should not be prodded again while completion settles.

## Deferred Work

- Dedicated heartbeat/nudge history tables remain deferred.
- YAML runtime policy documents remain descriptive inputs only; the active enforcement threshold still comes from runtime config in this stage.
