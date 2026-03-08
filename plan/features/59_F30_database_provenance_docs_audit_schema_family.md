# Phase F30A: Database Provenance, Documentation, And Audit Schema Family

## Goal

Implement the PostgreSQL schema family for provenance, rationale, documentation, review/testing outcomes, merges, and audit trails.

## Scope

- Database: define tables, constraints, indexes, and migrations for code provenance links, rationale records, source-document lineage, documentation artifacts, validation/review/testing results, merge records, rectification history, and audit events.
- CLI: expose query surfaces for provenance lookup, rationale traversal, docs inspection, review/testing history, merge history, and audit export.
- Daemon: persist all quality gates, merge outcomes, and provenance updates as first-class durable records.
- YAML: align validation/review/testing/docs identities with stored result records.
- Prompts: ensure review/testing/docs prompts can be tied back to durable result and rationale records.
- Tests: exhaustively test lineage integrity, rationale linkage, artifact versioning, merge/audit persistence, and every foreign-key or uniqueness rule.
- Performance: benchmark provenance lookup, audit-history scans, and documentation artifact retrieval paths.
- Notes: update provenance/audit/docs notes when storage structure or query semantics need clarification.

## Exit Criteria

- auditability, provenance, and documentation persistence are explicit, queryable, and fully test-backed.
