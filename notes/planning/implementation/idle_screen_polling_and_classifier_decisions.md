# Idle Screen Polling And Classifier Decisions

## Scope implemented in this slice

- Added a concrete screen-state classifier for primary sessions.
- Reused existing tmux/fake-session polling to classify screen state as `active`, `quiet`, or `idle`.
- Persisted classifier evidence through durable `session_events` using `screen_polled`.
- Exposed live classifier output on session read surfaces and nudge responses.

## Key implementation decisions

- The classifier uses pane-hash comparison plus idle-threshold timing rather than only `last_activity_at`.
- `quiet` is a deliberate middle state:
  - unchanged pane below the idle threshold
  - stable panes that have not yet crossed the idle threshold, including alt-screen captures
- `idle` is reserved for unchanged panes past the idle threshold, including first-sample cases where the threshold is already exceeded and stable alt-screen captures with no active-work markers.
- Daemon-originated nudge text is treated as non-progress for the next classifier step so repeated bounded nudge behavior does not reset itself.

## Boundaries kept in place

- This slice does not introduce an autonomous background polling loop; it freezes the classifier and evidence model first.
- `session_events` remain the durable audit surface for polling/nudge reasoning instead of adding a dedicated screen-history table.
- Recovery classification still uses the existing resumability/tmux-existence model; this slice primarily strengthens idle and operator inspection semantics.

## Deferred work

- Always-on background polling remains deferred.
- More advanced pane-diff heuristics beyond hash comparison remain deferred.
- Project-level runtime-policy expansion for dedicated poll windows remains deferred; the current implementation reuses existing session polling config.
