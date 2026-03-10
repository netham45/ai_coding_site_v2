# tmux Session Manager Decisions

## Scope implemented in this slice

- Added a concrete session-manager layer for primary and pushed-child tmux sessions.
- Replaced placeholder one-shot launch commands with long-lived interactive shell launch plans.
- Exposed richer tmux session metadata through daemon session reads and session events.
- Added duplicate active primary-session detection for bind and attach flows.

## Key implementation decisions

- tmux session names are now derived from durable run/session identity, not just the logical node id.
- The runtime now treats the tmux launch plan as code-owned behavior:
  - launch command
  - working directory
  - tmux attach command
- Primary-session and replacement-session creation both record launch metadata in durable session events.
- Pushed-child sessions reuse the same launch-plan approach so real tmux backends do not immediately exit before delegated prompts are sent.

## Boundaries kept in place

- This slice does not add a new session table or tmux-specific migration; existing `sessions` and `session_events` remain the durable authority.
- The CLI still talks to the daemon instead of attaching directly on its own; direct operator tmux-control ergonomics remain a later surface.
- Provider-process orchestration remains staged; the concrete implementation here launches the managed interactive shell reliably and leaves higher-level provider bootstrapping to later slices.

## Deferred work

- Dedicated heartbeat-history persistence remains deferred.
- Richer direct attach/control commands beyond the current daemon-backed inspection/mutation surfaces remain deferred to the later tmux command-surface phase.
