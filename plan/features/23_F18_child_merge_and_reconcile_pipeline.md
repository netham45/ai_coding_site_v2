# Phase F18: Child Merge And Reconcile Pipeline

## Goal

Merge child finals deterministically and reconcile parent output safely.

## Scope

- Database: merge ordering, reconcile results, post-merge stage results.
- CLI: merge order, child finals, and reconcile inspection.
- Daemon: deterministic merge execution and parent-local reconcile flow.
- YAML: reconcile task definitions and merge-related subtasks.
- Prompts: parent-local reconcile prompts.
- Tests: exhaustive ordering, reconcile no-op/change, and failed reconcile coverage.
- Performance: benchmark repeated merge/reconcile runs.
- Notes: update merge/reconcile notes if ordering fields expand.
