# Phase S08: Alembic Migration Discipline

## Goal

Freeze the migration workflow and discipline for schema evolution.

## Scope

- Database: define Alembic env structure, revision naming rules, migration review rules, and bootstrap/upgrade/downgrade expectations.
- CLI: provide developer/admin migration utility entrypoints where appropriate.
- Daemon: ensure startup checks can validate schema compatibility safely.
- YAML: no YAML semantics.
- Prompts: no prompt semantics.
- Tests: exhaustively test migration ordering, repeatability, fresh-bootstrap behavior, and upgrade-path safety.
- Performance: benchmark migration startup checks and representative migration execution paths.
- Notes: update database notes if migration discipline requires stricter constraints.

## Exit Criteria

- migration authoring and application rules are explicit and test-backed.
