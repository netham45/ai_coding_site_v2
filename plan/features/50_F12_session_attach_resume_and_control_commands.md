# Phase F12-S2: Session Attach, Resume, And Control Commands

## Goal

Implement the CLI command family for active session control.

## Rationale

- Rationale: Session binding only becomes practical when operators and AI clients can inspect, attach to, resume, and nudge the active session through explicit commands.
- Reason for existence: This phase exists to turn the session model into an actionable control surface instead of a passive record.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/16_F12_session_binding_and_resume.md`: F12 is the parent feature for these session commands.
- `plan/features/17_F34_provider_agnostic_session_recovery.md`: F34 shapes recovery and replacement-session behavior exposed here.
- `plan/features/39_F12_tmux_session_manager.md`: F12-S1 provides the concrete session backend these commands operate on.
- `plan/features/18_F13_idle_detection_and_nudge_behavior.md`: F13 uses some of the same control surfaces for nudging and inspection.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#cli-and-inspection-surfaces`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#recovery-classification-and-actions`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#backend-abstraction-and-test-posture`

## Scope

- Database: ensure session control operations have durable event and current-state backing.
- CLI: implement:
  - `session show`
  - `session events`
  - `session attach`
  - `session resume`
  - `session nudge`
- Daemon: validate attach/resume/control semantics and maintain authoritative session ownership.
- YAML: runtime policy only.
- Prompts: session-control prompts must align with actual session-control commands.
- Tests: exhaustively cover attach/resume/nudge semantics, invalid-control attempts, and authority conflicts.
- Performance: benchmark session-control command latency.
- Notes: update session CLI notes if control surfaces evolve.
