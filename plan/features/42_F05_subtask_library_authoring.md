# Phase F05-S1: Subtask Library Authoring

## Goal

Author the full reusable built-in subtask library and make its packaging choice explicit.

## Scope

- Database: no major new structures beyond lineage and compile persistence.
- CLI: expose subtask-chain inspection clearly enough to validate authored subtasks.
- Daemon: compile and dispatch every built-in subtask type deterministically.
- YAML: author every required built-in subtask definition or explicitly freeze the inline-template strategy.
- Prompts: ensure subtask prompt-bearing fields are bound to the prompt pack and rendering model.
- Tests: exhaustively cover every built-in subtask definition for schema validity, compileability, dispatchability, and handler compatibility.
- Performance: benchmark dispatch and compile cost across the authored subtask catalog.
- Notes: update the YAML built-ins checklist and any subtask packaging notes as the choice is finalized.
