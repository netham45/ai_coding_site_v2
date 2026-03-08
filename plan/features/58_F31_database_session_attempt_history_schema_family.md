# Phase F31B: Database Session, Attempt, And History Schema Family

## Goal

Implement the PostgreSQL schema family for execution attempts, tmux/provider sessions, prompt history, summaries, nudges, failures, and recovery.

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
