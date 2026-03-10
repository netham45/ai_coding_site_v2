# Database Session Attempt History Schema Family Decisions

This note records the implementation boundary for `plan/features/58_F31_database_session_attempt_history_schema_family.md`.

## Decisions

1. The base session, attempt, prompt, summary, and gate-result tables already existed before this phase. This slice focused on the missing schema-family normalization around them: current/history SQL views, composite history indexes, and schema-level session-shape constraints.
2. The schema now materializes these history/current-state views directly: `latest_subtask_attempts`, `active_primary_sessions`, `latest_validation_results`, `latest_review_results`, and `latest_test_results`.
3. Composite indexes were added for the hottest history reads rather than leaving those views as convenience wrappers over repeated scans. The current slice adds composite indexes for latest-attempt lookup, latest gate-result lookup, session inspection, and node-scoped prompt/summary history reads.
4. The `sessions` table now enforces the documented role/parent shape at the schema level: `primary` sessions must have no parent, and `pushed_child` sessions must reference a parent session.
5. Duplicate active primary sessions remain application-detected rather than DB-rejected. That is deliberate so recovery tests and daemon logic can still surface ambiguous ownership as an auditable runtime condition instead of turning it into a blind insert failure.
6. No YAML semantics changed in this phase. No prompt semantics changed in this phase.

## Notes Alignment

- The database spec now marks the session/attempt/current-history views as materialized instead of deferred.
- The current implementation still treats `sessions` and `session_events` as the canonical ownership/history records; the new views are read surfaces, not separate sources of truth.
