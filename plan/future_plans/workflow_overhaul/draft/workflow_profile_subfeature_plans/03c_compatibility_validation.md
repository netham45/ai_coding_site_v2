# Workflow Profile Subfeature Plan 03c: Compatibility Validation

## Parent Area

- `03 Layout-Definition Extension`

## Parent Slice

- `draft_feature_plans/01_workflow_profile_yaml_family_and_structural_validation.md`
- `draft_feature_plans/03_profile_aware_layout_resolution_and_child_materialization.md`

## Goal

Validate layout compatibility against node kinds and child workflow profiles.

## Implementation Subtasks

- validate top-level layout compatibility with node kind and profile ids
- validate child `workflow_profile` references against child node kinds and supported profiles
- add failure messages that clearly identify the broken layout entry and conflicting metadata
