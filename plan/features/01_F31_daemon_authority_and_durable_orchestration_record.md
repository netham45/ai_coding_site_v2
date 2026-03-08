# Phase F31: Daemon Authority And Durable Orchestration Record

## Goal

Make the daemon the live orchestration authority while keeping all critical state durable and inspectable.

## Scope

- Database: durable authority-related state, mutation history, current-state views.
- CLI: route mutating operations through the daemon instead of direct state mutation.
- Daemon: request validation, mutation authorization, durable-write sequencing, authoritative orchestration boundary.
- YAML: no new semantics beyond config/bootstrap references.
- Prompts: reserve prompt issuance linkage in orchestration records.
- Tests: exhaustively cover legal mutations, illegal mutations, race-sensitive writes, and recoverability.
- Performance: benchmark hot mutation and current-state read paths.
- Notes: update authority notes if implementation changes API/process assumptions.
