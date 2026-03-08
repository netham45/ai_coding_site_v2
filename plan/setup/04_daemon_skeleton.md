# Phase S04: Daemon Skeleton

## Goal

Create the initial Python daemon process and mutation boundary.

## Scope

- Database: wire transaction boundaries and durable-write helpers.
- CLI: establish client-to-daemon request path for future mutating commands.
- Daemon: create server lifecycle, request validation skeleton, health/status surface, and background-task scaffolding.
- YAML: no compile logic yet beyond resource bootstrap hooks.
- Prompts: no prompt execution yet beyond resource bootstrap hooks.
- Tests: exhaustively test daemon startup, shutdown, request validation scaffolding, and DB-unavailable behavior.
- Performance: benchmark daemon boot and baseline request overhead.
- Notes: update daemon/authority notes if actual process topology changes.

## Exit Criteria

- daemon runs, can be health-checked, and can serve as the future mutation authority.
