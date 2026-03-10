# Phase F12: Session Binding And Resume

## Goal

Bind one authoritative session to one active run and support safe resume/reattach behavior.

## Rationale

- Rationale: Active work becomes unsafe if multiple sessions can appear authoritative for the same run or if session ownership is ambiguous after interruption.
- Reason for existence: This phase exists to define one authoritative session binding model with explicit resume and reattach semantics.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/04_F07_durable_node_lifecycle_state.md`: F07 defines run state the active session is bound to.
- `plan/features/13_F09_node_run_orchestration.md`: F09 uses session ownership to protect active execution.
- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`: F31 owns the authoritative binding mutation path.
- `plan/features/17_F34_provider_agnostic_session_recovery.md`: F34 handles recovery when the original provider identity is unreliable.
- `plan/features/39_F12_tmux_session_manager.md`: F12-S1 is the concrete tmux-backed implementation slice.
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`: F12-S2 exposes attach, resume, and control commands.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `notes/planning/implementation/tmux_and_session_harness_decisions.md`

## Scope

- Database: primary session binding, session status, session events, run/session linkage.
- CLI: bind, attach, resume, show-current, and session-inspection surfaces.
- Daemon: authoritative session binding and safe reattachment behavior.
- YAML: runtime policy only; binding logic remains code-owned.
- Prompts: session bootstrap prompt aligned with actual command loop.
- Tests: exhaustive single-session, detached-session, invalid-bind, and durable-history coverage.
- Performance: benchmark heartbeat and lookup paths.
- Notes: update session notes if tmux/provider integration needs stronger abstractions.
