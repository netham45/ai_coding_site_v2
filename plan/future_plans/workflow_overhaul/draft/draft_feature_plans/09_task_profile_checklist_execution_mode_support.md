# Feature 09: Task Profile Checklist Execution Mode Support

## Goal

Allow task-oriented workflow profiles to opt into checklist execution mode instead of introducing a new semantic task type.

## Main Work

- add `execution_mode`
- attach checklist contract references to applicable profiles
- freeze checklist-mode context into compiled workflow state

## Implementation Subtasks

- add `execution_mode` and checklist contract fields to applicable task-oriented profile definitions
- distinguish profile-level checklist support from instance-level checklist attachment data
- freeze checklist-mode metadata into compiled workflow context when checklist execution is selected
- define how startup, creation, or orchestration select checklist mode for a concrete task instance

## Main Dependencies

- Setup 01
- Setup 02
- Feature 08

## Flows Touched

- `01_create_top_level_node_flow`
- `02_compile_or_recompile_workflow_flow`

## Relevant Current Code

- `src/aicoding/daemon/workflows.py`
- `src/aicoding/daemon/run_orchestration.py`
- `src/aicoding/db/models.py`
- `src/aicoding/resources/yaml/builtin/system-yaml/nodes/`

## Current Gaps

- current compile and runtime state has no `execution_mode` concept
- checklist mode is not selectable from workflow profiles or frozen into compiled state
