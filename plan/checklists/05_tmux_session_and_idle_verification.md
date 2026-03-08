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
