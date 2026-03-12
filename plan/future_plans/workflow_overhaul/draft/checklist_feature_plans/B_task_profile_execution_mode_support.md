# Slice B: Task/Profile Execution-Mode Support

## Goal

Allow task-oriented workflow profiles to opt into checklist execution mode.

## Main Work

- add `execution_mode`
- attach checklist contract references to profiles
- freeze checklist-mode context into compiled workflow state

## Systems

- Database: planned
- CLI: partial
- Daemon: primary
- YAML: primary
- Prompts: partial
- Website UI: not_applicable

## Main Risks

- turning checklist into a semantic task type
- unclear split between profile-level support and instance-level checklist data
