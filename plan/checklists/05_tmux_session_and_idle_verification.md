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

- 2026-03-10: The live primary-session tmux launch path is now Codex-backed for fresh bind and provider-agnostic recovery, but there is not yet dedicated real E2E proof for primary-session Codex launch, idle, nudge, repeated-idle, and live completion/failure behavior.
- 2026-03-10: Child-session launch still uses the long-lived interactive shell launch plan, so child-session tmux/Codex proof remains a separate gap from the primary-session runtime path.
- 2026-03-10: The first real primary-session launch E2E passes only when it asserts on the pane process command line rather than `pane_current_command`; the tmux pane command name is too weak a signal because the Codex path includes a bootstrap helper and the installed `codex` entrypoint is Node-based.
- 2026-03-10: The prompt-bootstrap E2E currently fails because the bound primary tmux session may exit before the recorded `prompt_log_path` is written, which blocks the intended idle/nudge/repeated-idle runtime narrative.
