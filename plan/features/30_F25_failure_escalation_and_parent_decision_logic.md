# Phase F25: Failure Escalation And Parent Decision Logic

## Goal

Handle child and subtask failures compositionally through durable parent decisions.

## Scope

- Database: failure classes, summaries, parent counters, parent decisions.
- CLI: failure history and parent-decision inspection.
- Daemon: child-failure classification plus retry/replan/pause behavior.
- YAML: declarative retry/pause thresholds only; decisions remain code-owned.
- Prompts: parent pause-for-user and parent-local replan prompts.
- Tests: exhaustive coverage for every failure class and parent-decision outcome.
- Performance: benchmark repeated failure-handling and counter-update paths.
- Notes: update parent-failure notes if the taxonomy expands.
