# Phase F34: Provider-Agnostic Session Recovery

## Goal

Recover runs using durable state even when provider session identity is absent or unreliable.

## Rationale

- Rationale: Provider-specific session identifiers are not reliable enough to serve as the sole recovery mechanism for long-lived orchestration.
- Reason for existence: This phase exists so the system can recover from lost or changed provider identity by leaning on durable runtime state instead of fragile external handles.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/16_F12_session_binding_and_resume.md`: F12 defines the primary session model recovery must restore or replace.
- `plan/features/39_F12_tmux_session_manager.md`: F12-S1 provides one of the concrete session backends recovery has to reason about.
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`: F12-S2 is how operators and clients invoke recovery-related control paths.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/pseudocode/modules/recover_interrupted_run.md`

## Scope

- Database: recovery-critical state and recovery event history.
- CLI: recovery-oriented inspect and resume flows.
- Daemon: recovery classification, replacement-session creation, and safe resume.
- YAML: configurable recovery policy only.
- Prompts: resume-existing and replacement-session prompts.
- Tests: exhaustive healthy, stale, lost-tmux, no-provider, and non-resumable recovery coverage.
- Performance: benchmark recovery-path latency.
- Notes: update recovery appendix if implementation reveals new recovery classes.
