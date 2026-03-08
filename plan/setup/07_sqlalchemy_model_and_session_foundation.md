# Phase S07: SQLAlchemy Model And Session Foundation

## Goal

Establish the default SQLAlchemy usage pattern for models, sessions, transactions, and query boundaries.

## Scope

- Database: define model base, metadata ownership, session factory pattern, transaction helpers, and sync PostgreSQL access conventions.
- CLI: ensure CLI code can reuse safe session/query helpers.
- Daemon: ensure daemon request handling uses consistent DB session boundaries.
- YAML: no new YAML semantics.
- Prompts: no prompt semantics beyond reserving prompt-history model integration points.
- Tests: exhaustively test session lifecycle, transaction rollback behavior, nested transaction expectations, and DB helper misuse cases.
- Performance: benchmark session creation, transaction overhead, and representative hot query patterns.
- Notes: update DB implementation notes if actual SQLAlchemy usage diverges from assumptions.

## Exit Criteria

- SQLAlchemy usage conventions are explicit, testable, and reusable across the codebase.
