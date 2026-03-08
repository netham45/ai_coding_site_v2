# Phase S01: Database Bootstrap

## Goal

Stand up the PostgreSQL foundation for all later features.

## Scope

- Database: configure PostgreSQL, SQLAlchemy, Alembic, connection helpers, transaction helpers, and test-database lifecycle.
- CLI: add basic DB health/debug commands.
- Daemon: wire configuration and connection pooling into the daemon skeleton.
- YAML: no feature YAML yet beyond config references.
- Prompts: no runtime prompts yet; reserve prompt-history DB integration points.
- Tests: exhaustively test migrations, connection failure handling, rollback safety, fixture reset, and concurrent-test isolation.
- Performance: benchmark connection startup, migration runtime, common bootstrap queries, and synchronous DB access under expected request concurrency.
- Notes: update DB notes if real migration/tooling constraints change assumptions.

## Exit Criteria

- PostgreSQL runs locally and in CI.
- migrations are repeatable.
- tests can create, reset, and isolate databases safely.
