# Setup 01: Schema And Builtin Asset Readiness

## Goal

Prepare the schema and built-in asset posture for workflow profiles, profile-aware layouts, prompt references, and checklist-mode assets.

## Main Work

- freeze schema-family direction for workflow profiles and checklist mode
- freeze built-in asset layout for starter profiles, rich layouts, prompt assets, and example checklist assets
- define validation expectations for cross-references

## Main Outputs

- schema-readiness checklist
- builtin-asset adoption order
- validation boundary decisions

## Implementation Subtasks

- freeze the intended schema families for workflow profiles, layouts, prompt refs, checklist templates, and checklist instances
- define how starter workflow profiles, rich layouts, prompts, and checklist examples will map into real builtin asset directories
- decide which cross-reference rules must be validated mechanically across kinds, profiles, layouts, and checklist templates
- identify which existing builtin assets can be reused versus which must be replaced when workflow-overhaul lands

## Main Dependencies

- Setup 00

## Flows Touched

- `02_compile_or_recompile_workflow_flow`
- `03_materialize_and_schedule_children_flow`

## Relevant Current Code

- `src/aicoding/yaml_schemas.py`
- `src/aicoding/structural_library.py`
- `src/aicoding/overrides.py`
- `src/aicoding/resources/yaml/builtin/system-yaml/nodes/`
- `src/aicoding/resources/yaml/builtin/system-yaml/tasks/`

## Current Gaps

- there is no real `workflow_profile_definition` or checklist schema family in `src/aicoding/yaml_schemas.py`
- builtin node and task assets are still the active source of workflow shape, with no profile-aware asset loading path
