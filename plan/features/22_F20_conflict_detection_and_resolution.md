# Phase F20: Conflict Detection And Resolution

## Goal

Persist merge conflicts durably and halt or resume safely through resolution.

## Scope

- Database: conflict records, conflict resolution state, operator decisions.
- CLI: conflict inspection and resolution surfaces.
- Daemon: conflict detection during merge/rectification and safe halt behavior.
- YAML: conflict-handling policy inputs and optional conflict-resolution task hooks.
- Prompts: conflict pause/guidance prompts when operator action is required.
- Tests: exhaustive conflict detection, blocked progression, and resumed resolution coverage.
- Performance: benchmark conflict inspection paths.
- Notes: update conflict notes if extra states are needed.
