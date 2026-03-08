# Flow 07: Pause, Resume, And Recover

## Purpose

Pause work intentionally, resume safe work, or recover interrupted work after session or host disruption.

## Covers journeys

- pause a node
- resume a paused node
- recover after session loss or tmux loss
- nudge idle work

## Entry conditions

- a node has an active or paused run, or recovery is requested for a known node version

## Task flow

1. load authoritative run state and active primary session
2. inspect resumability, current cursor, heartbeat freshness, and tmux/provider state
3. classify the session as healthy, detached, stale, lost, or ambiguous
4. if pausing, persist pause reason and pause event
5. if resuming, prefer reusing a healthy authoritative session
6. if the session is lost but the run is resumable, create a replacement session
7. if git/cursor/session ownership is ambiguous, refuse unsafe resume and pause for intervention
8. reload the current subtask into the recovered session
9. persist recovery event history

## Required subtasks

- `load_run_and_session_state`
- `classify_session_health`
- `validate_resume_safety`
- `persist_pause_event_if_requested`
- `reuse_session_if_safe`
- `create_replacement_session_if_needed`
- `reload_current_cursor_context`
- `persist_recovery_decision`

## Required capabilities

- `ai-tool node pause ...`
- `ai-tool node resume ...`
- `ai-tool session resume ...`
- `ai-tool session attach ...`
- `ai-tool session nudge ...`
- duplicate-session detection
- git-head safety validation

## Durable outputs

- pause events
- recovery events
- session status transitions
- replacement session linkage
- resumed cursor state

## Failure cases that must be supported

- non-resumable run
- duplicate active primary sessions
- git head mismatch
- stale but still running tmux session
- lost session with broken cursor state

## Completion rule

The system either resumes safely from durable state or explains exactly why automatic recovery was refused.
