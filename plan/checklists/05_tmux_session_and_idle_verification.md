# Checklist C05: tmux, Session, And Idle Verification

## Goal

Verify that tmux-backed session management, screen polling, idle detection, and recovery behave as designed.

## Verify

- tmux sessions are created and named deterministically
- session records match tmux-backed reality
- idle detection uses the intended polling/classifier behavior
- nudges, pause paths, and recovery paths are all durable and inspectable

## Tests

- exhaustive tmux/session/idle/recovery tests
- performance checks for polling overhead and recovery latency

## Notes

- update session, recovery, and idle notes if the implemented mechanics differ from assumptions

## Discovered Issues

- 2026-03-10: The live primary-session tmux launch path still targets an interactive shell rather than a real Codex session, so the requested Codex-launch E2E proof cannot pass until that runtime path changes.
- 2026-03-10: The requested dedicated tmux/Codex E2E files for live launch/idle/nudge and live completion/failure do not exist yet; current strongest idle/nudge proof remains in fake-adapter tests.
