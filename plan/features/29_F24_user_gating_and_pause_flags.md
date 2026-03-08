# Phase F24: User Gating And Pause Flags

## Goal

Support explicit pause points, approval gates, and safe resume behavior.

## Scope

- Database: pause flags, pause summaries, pause-event history.
- CLI: pause-state, approval, and resume flows.
- Daemon: enforce pause transitions and prevent silent skip on resume.
- YAML: gate declarations and gate policies.
- Prompts: pause-for-user and approval-handoff prompts.
- Tests: exhaustive pause entry, pause clearing, approval-required, and illegal-resume coverage.
- Performance: benchmark pause-state query paths.
- Notes: update pause-event notes if event granularity changes.
