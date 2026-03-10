# Idle Detection And Nudge Behavior Decisions

## Scope

This note records the implementation boundary for `plan/features/18_F13_idle_detection_and_nudge_behavior.md`.

## Decisions

- Idle detection is now derived from the existing session poller plus the canonical durable primary session record, not from a new heartbeat-history schema.
- No new migration was added in this slice. Idle audit is staged through `session_events`, and pause escalation remains canonical in durable run state.
- `session nudge --node <id>` now exists as a daemon-backed command that inspects the active primary session, suppresses false positives when alt-screen content is active, and records durable nudge events.
- The current bounded nudge policy is runtime-configured through `AICODING_SESSION_IDLE_THRESHOLD_SECONDS` and `AICODING_SESSION_MAX_NUDGE_COUNT`.
- The final allowed nudge uses stronger repeated-missed-step prompt text before any later pause escalation.
- Once the nudge budget is exhausted, the daemon pauses the run with `pause_flag_name = "idle_nudge_limit_exceeded"` instead of nudging indefinitely.

## Deferred Work

- Dedicated heartbeat/nudge history tables remain deferred.
- Background polling loops remain placeholder-level; this slice exposes the authoritative nudge behavior and audit path but does not yet run autonomous daemon polling.
- YAML runtime policy documents remain descriptive inputs only; the active enforcement threshold still comes from runtime config in this stage.
