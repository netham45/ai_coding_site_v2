# Phase F09: Node Run Orchestration

## Goal

Implement the authoritative run loop for compiled nodes.

## Scope

- Database: node runs, run state, cursor, attempts, run history.
- CLI: current task/subtask, attempt state, workflow advancement.
- Daemon: admit-or-load, loop ownership, cursor advancement, acceptance of stage completion.
- YAML: executable task/subtask ordering and acceptance contracts.
- Prompts: compiled execution prompts tied to real stage behavior.
- Tests: exhaustive happy, pause, failure, retry, and cursor-integrity coverage.
- Performance: benchmark hot loop operations.
- Notes: update runtime loop notes if ownership shifts during coding.
