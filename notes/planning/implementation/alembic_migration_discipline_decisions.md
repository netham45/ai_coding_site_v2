# Alembic Migration Discipline Decisions

## Purpose

Capture implementation choices made while completing `plan/setup/08_alembic_migration_discipline.md`.

## Decisions

### Revision discipline

- migration files continue to live in `alembic/versions`
- revision identifiers are constrained to `NNNN_slug_name`
- the repository currently assumes a single linear Alembic head and treats multi-head drift as an error in migration inspection helpers

### CLI and daemon posture

- admin CLI now exposes `upgrade`, `downgrade`, `heads`, `history`, and `check-schema` commands for migration inspection and control
- daemon DB status now exposes schema compatibility explicitly instead of assuming the live database matches the packaged migration head
- compatibility checks remain read-only and safe to run during startup/status inspection

### Test and performance posture

- migration discipline is covered by unit tests for revision naming and history, integration tests for bootstrap and compatibility transitions, and CLI/daemon coverage for operator-facing inspection paths
- performance checks now include expected-head lookup and schema-compatibility probes so migration safety checks remain lightweight

### YAML and prompt posture

- this phase intentionally adds no YAML semantics
- this phase intentionally adds no prompt semantics
