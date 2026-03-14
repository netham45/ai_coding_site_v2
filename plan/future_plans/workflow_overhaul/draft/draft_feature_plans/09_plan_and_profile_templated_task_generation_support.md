# Feature 09: Plan And Profile Templated Task Generation Support

## Goal

Allow plans and applicable workflow profiles to reference reusable task-sequence templates instead of only authoring one-off child tasks.

## Main Work

- add template-reference support
- define selection rules for one-off versus templated decomposition
- freeze template provenance into compiled workflow state

## Implementation Subtasks

- add template-reference fields to the applicable planning or profile surfaces
- define when startup or compile may select a template for a concrete node
- distinguish authored child tasks from template-generated child tasks in compiled state
- freeze template metadata and step lineage into compile outputs

## Main Dependencies

- Setup 01
- Setup 02
- Feature 08

## Flows Touched

- `01_create_top_level_node_flow`
- `02_compile_or_recompile_workflow_flow`

## Relevant Current Code

- `src/aicoding/daemon/workflows.py`
- `src/aicoding/daemon/workflow_start.py`
- `src/aicoding/resources/yaml/builtin/system-yaml/nodes/`

## Current Gaps

- current compile and runtime state has no reusable template-reference concept for child generation
- the plan bundle assumes one-off child authoring or a now-superseded checklist execution mode
