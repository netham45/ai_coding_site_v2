# Database Runtime State Schema Family Decisions

This note records the implementation boundary for `plan/features/57_F31_database_runtime_state_schema_family.md`.

## Decisions

1. The runtime-state base tables were already present before this phase, so this slice focused on the missing schema-normalization pieces around them: current-state SQL views, composite runtime indexes, and schema-test coverage.
2. The schema now materializes these runtime-state views directly: `active_node_versions`, `authoritative_node_versions`, `candidate_node_versions`, `latest_node_runs`, `current_node_cursors`, `pending_dependency_nodes`, and `latest_parent_child_authority`.
3. The `admin db status` surface now reports database views as well as tables so operators can verify the runtime-state schema family without opening PostgreSQL manually.
4. Composite indexes were added for the new hot-path views instead of leaving them as convenience wrappers over repeated full scans. The first slice adds `(node_version_id, run_number)` on `node_runs` and `(node_version_id, created_at)` on `node_dependency_blockers`.
5. Session-owned current-state views such as `active_primary_sessions` remain intentionally deferred to the companion session/attempt-history schema-family slice. This keeps runtime-node/run state separate from canonical session ownership modeling.
6. No YAML semantics changed in this phase. No prompt semantics changed in this phase.

## Notes Alignment

- The database spec now explicitly states which runtime-state views are materialized now and which session/result-family views remain deferred.
- The implementation keeps daemon/runtime behavior on the same authoritative tables it already used; this phase improves SQL-level inspectability and read efficiency rather than moving coordination logic into the database.
