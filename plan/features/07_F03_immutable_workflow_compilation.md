# Phase F03: Immutable Workflow Compilation

## Goal

Compile mutable YAML and prompt references into immutable executable workflows.

## Scope

- Database: compiled workflow/task/subtask tables and compile-failure persistence.
- CLI: compiled workflow and compile-failure inspection.
- Daemon: deterministic compile pipeline and persisted artifacts.
- YAML: source-to-compiled transformation for all execution families.
- Prompts: freeze prompt references into compiled workflow snapshots.
- Tests: exhaustive deterministic compile, failure-class, and bad-reference coverage.
- Performance: benchmark compile cost and repeated compile scenarios.
- Notes: update compile notes if implementation needs extra pipeline stages.
