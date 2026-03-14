# Feature 08: Task-Sequence Template Family

## Goal

Adopt reusable task-sequence templates as validated authoring assets for generating normal child tasks.

## Main Work

- add task-sequence schema models
- validate step dependency structure and template applicability
- define template materialization vocabulary without adding a second runtime lifecycle

## Implementation Subtasks

- add real schema models for `task_sequence_schema_definition` and `task_sequence_template`
- validate step ids, dependency references, task-profile references, and objective fields
- define the allowed materialization posture for template-driven child generation
- constrain template fields so generated tasks remain ordinary tasks with ordinary runtime semantics

## Main Dependencies

- Setup 00
- Setup 01

## Flows Touched

- `02_compile_or_recompile_workflow_flow`

## Relevant Current Code

- `src/aicoding/yaml_schemas.py`
- `src/aicoding/structural_library.py`
- `src/aicoding/resources/yaml/`

## Current Gaps

- there is no task-sequence template family in current YAML validation code
- there is no reusable decomposition asset that compiles directly into normal child tasks
