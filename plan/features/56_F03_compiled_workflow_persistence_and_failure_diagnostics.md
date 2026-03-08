# Phase F03-S7: Compiled Workflow Persistence And Failure Diagnostics

## Goal

Persist compiled workflows and compile failures cleanly as the final compiler stage.

## Scope

- Database: persist compiled workflows, compiled tasks/subtasks, compile-stage diagnostics, and compile-failure records.
- CLI: inspect compiled workflow artifacts and stage-specific failure diagnostics.
- Daemon: finalize compile output persistence and reject partial/invalid outputs.
- YAML: no new semantics beyond compiled artifact mapping.
- Prompts: ensure compiled prompt references remain inspectable in persisted output.
- Tests: exhaustively cover successful persistence, partial failure rollback, and stage-specific diagnostics.
- Performance: benchmark persistence overhead for large workflows.
- Notes: update compile-failure and traceability notes if diagnostics expand.
