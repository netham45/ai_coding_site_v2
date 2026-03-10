# Phase F12-S1: tmux Session Manager

## Goal

Implement the concrete tmux-backed session manager used for active runs.

## Rationale

- Rationale: Session binding is abstract until the runtime has a concrete terminal/session backend that can be created, reattached, and inspected.
- Reason for existence: This phase exists to make tmux-backed session management a real implementation surface with durable linkage to runs.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/16_F12_session_binding_and_resume.md`: F12 is the parent feature for concrete session management.
- `plan/features/17_F34_provider_agnostic_session_recovery.md`: F34 handles failures or missing identity from this backend.
- `plan/features/18_F13_idle_detection_and_nudge_behavior.md`: F13 polls and nudges against the active tmux session.
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`: F12-S2 is the command surface used to operate tmux-backed sessions.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#tmux-session-model`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#primary-session-lifecycle`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#recovery-classification-and-actions`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#backend-abstraction-and-test-posture`
- `notes/scenarios/journeys/common_user_journeys_analysis.md`

## Scope

- Database: persist tmux session identity, linkage to node run/session records, and relevant events.
- CLI: implement session attach/show/resume behavior that understands tmux-backed sessions.
- Daemon: create and manage tmux sessions per task/run GUID, launch provider processes, and keep session identity authoritative.
- YAML: runtime policy may configure tmux-related limits, but tmux management remains code-owned.
- Prompts: ensure session bootstrap prompts match the real tmux-backed session lifecycle.
- Tests: exhaustively cover tmux session creation, attachment, missing tmux sessions, duplicate-session detection, and session record consistency.
- Performance: benchmark tmux session creation and attach/reattach overhead.
- Notes: update tmux/session notes if implementation forces naming or lifecycle changes.
