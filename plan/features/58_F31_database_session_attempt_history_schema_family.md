# Phase F31B: Database Session, Attempt, And History Schema Family

## Goal

Implement the PostgreSQL schema family for execution attempts, tmux/provider sessions, prompt history, summaries, nudges, failures, and recovery.

## Rationale

- Rationale: Session recovery, prompt auditability, and failure analysis all depend on durable attempt and session history at the database layer.
- Reason for existence: This phase exists to model the execution-history records that make long-running sessions recoverable and inspectable.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`: F31 is the parent authority feature for this schema family.
- `plan/features/16_F12_session_binding_and_resume.md`: F12 uses these tables to store active session bindings and resume state.
- `plan/features/17_F34_provider_agnostic_session_recovery.md`: F34 relies on this history to recover interrupted runs.
- `plan/features/31_F28_prompt_history_and_summary_history.md`: F28 stores prompt and summary history in this general schema area.
- `plan/features/57_F31_database_runtime_state_schema_family.md`: F31A holds the complementary live runtime-state tables.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/database/database_schema_spec_v2.md`
- `notes/planning/expansion/database_schema_v2_expansion.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `notes/contracts/persistence/pause_workflow_event_persistence.md`

## Scope

- Database: define tables, constraints, indexes, and migrations for attempts, session bindings, provider resume identifiers, screen-poll snapshots or references, idle/nudge history, prompt deliveries, summaries, failure reports, and recovery events.
- CLI: expose query surfaces for current session state, attempt history, prompt history, summary history, and recovery diagnostics.
- Daemon: persist every session/attempt transition and recovery-critical record authoritatively.
- YAML: no new YAML semantics beyond aligning subtask/stage identities with persisted attempt history.
- Prompts: ensure delivered prompts, nudges, pause messages, and recovery prompts have durable traceability.
- Tests: exhaustively test attempt creation, session rebinding, resume identity handling, summary recording, idle detection history, failure persistence, and recovery-path durability.
- Performance: benchmark attempt-history writes, prompt-history retrieval, and session inspection paths.
- Notes: update runtime/session notes if the persistence model needs additional recovery-critical fields.

## Exit Criteria

- execution history and recovery state are durable, inspectable, and fully covered by tests.
