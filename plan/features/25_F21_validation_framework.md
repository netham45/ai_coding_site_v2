# Phase F21: Validation Framework

## Goal

Make validation a first-class gate for stage completion and finalization.

## Scope

- Database: validation result persistence and history.
- CLI: validation inspection and failure details.
- Daemon: authoritative validation gating before cursor advancement/finalization.
- YAML: validation definitions and references from tasks/subtasks.
- Prompts: missed-step and missing-output prompts tied to actual validation failures.
- Tests: exhaustive coverage for every validation type and failure class.
- Performance: benchmark validation execution over common workflows.
- Notes: update validation notes when new check types are discovered.
