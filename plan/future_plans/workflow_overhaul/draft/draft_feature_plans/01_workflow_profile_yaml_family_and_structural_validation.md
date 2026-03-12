# Feature 01: Workflow Profile YAML Family And Structural Validation

## Goal

Adopt `workflow_profile_definition` as a real schema family and validate it against node kinds, layouts, and builtin assets.

## Main Work

- add schema models
- extend node/layout schema contracts
- validate builtin profile and layout cross-references

## Implementation Subtasks

- add `workflow_profile_definition` to the real schema family registry and validation model set
- extend node definitions with supported/default profile metadata and freeze the field contract
- extend layout definitions with profile compatibility, role metadata, and child-profile hints
- teach structural-library validation to check builtin profile-to-kind, profile-to-layout, and child-profile cross-references

## Main Dependencies

- Setup 00
- Setup 01

## Flows Touched

- `02_compile_or_recompile_workflow_flow`
- `03_materialize_and_schedule_children_flow`

## Relevant Current Code

- `src/aicoding/yaml_schemas.py`
- `src/aicoding/structural_library.py`
- `src/aicoding/overrides.py`
- `src/aicoding/resources/yaml/builtin/system-yaml/nodes/epic.yaml`
- `src/aicoding/resources/yaml/builtin/system-yaml/nodes/phase.yaml`
- `src/aicoding/resources/yaml/builtin/system-yaml/nodes/plan.yaml`
- `src/aicoding/resources/yaml/builtin/system-yaml/nodes/task.yaml`

## Current Gaps

- no workflow-profile schema family exists in the active loader or validator
- node and layout schema do not currently carry the profile, role, and compatibility fields described by the draft notes
