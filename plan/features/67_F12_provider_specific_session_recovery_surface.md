# Phase F12-S3: Provider-Specific Session Recovery Surface

## Goal

Add explicit provider-specific recovery and session-restoration surfaces on top of the current provider-agnostic recovery model.

## Rationale

- Rationale: Provider-agnostic recovery is a strong baseline, but some recovery decisions may require provider-aware identity, restoration, or relaunch semantics to avoid overly generic handling.
- Reason for existence: This phase exists to make provider-aware recovery explicit and testable instead of forcing all sessions into the same abstracted recovery path forever.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/16_F12_session_binding_and_resume.md`: F12 established durable session ownership and bind/attach/resume state.
- `plan/features/17_F34_provider_agnostic_session_recovery.md`: F34 provides the current provider-agnostic recovery baseline that this phase extends.
- `plan/features/39_F12_tmux_session_manager.md`: F12-S1 provides the concrete backend that provider-specific recovery must coordinate with.
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`: F12-S2 defines the current command/control surface that may need provider-aware extensions.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#recovery-classification-and-actions`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`

## Scope

- Database: persist any additional provider session identity, restoration metadata, or provider-specific recovery events needed for auditability.
- CLI: expose provider-aware recovery inspection and control commands only where they materially differ from the provider-agnostic path.
- Daemon: classify and execute provider-specific recovery semantics safely while preserving the provider-agnostic fallback.
- YAML: keep provider-specific recovery ownership in code rather than policy YAML.
- Prompts: update recovery prompts if providers require distinct attach/resume/replace guidance.
- Tests: exhaustively cover healthy, detached, stale, lost, and provider-restorable cases, including fallback behavior.
- Performance: benchmark recovery classification and restoration overhead across provider-aware and provider-agnostic paths.
- Notes: update recovery, session, and bootstrap notes to describe the provider-aware boundary.
