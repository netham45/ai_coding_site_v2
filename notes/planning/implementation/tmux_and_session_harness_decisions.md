# tmux And Session Harness Decisions

## Purpose

Capture implementation choices made while completing `plan/setup/06_tmux_and_session_test_harness.md`.

## Decisions

### Harness abstraction

- tmux integration is isolated behind a session-adapter abstraction
- the repository now supports both `tmux` and deterministic `fake` session backends
- idle polling uses an injected clock so tests do not depend on wall-clock sleeps

### Daemon posture

- the daemon owns session harness state through app-managed adapter and poller instances
- placeholder session endpoints exist for bind, attach, resume, and show-current flows
- these endpoints scaffold the session authority path without claiming full durable session-state semantics yet

### Later tmux-manager follow-on

- the later concrete tmux-manager slice now replaces the original placeholder `printf` launch behavior for primary and pushed-child sessions with long-lived interactive shell launch plans
- tmux session names are now derived from durable run/session identity and surfaced back through daemon read paths
- bind and attach now reject duplicate active primary-session rows instead of silently picking one record
- session events now record launch metadata such as the tmux session name, launch command, working directory, and attach command

### Idle-classifier follow-on

- the later idle-screen slice now reuses the same adapter abstraction to capture pane text and compare pane hashes over time
- screen-state comparison evidence is persisted through `session_events` as `screen_polled` records rather than a separate poll-history table

### Test posture

- fake-session tests are the default deterministic path
- tmux lifecycle coverage is kept to a smoke-level adapter test so the suite verifies real integration without becoming timing-fragile
