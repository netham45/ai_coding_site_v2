# Workflow Profile Subfeature Plan 01b: Family Registration

## Parent Area

- `01 Schema Family Adoption`

## Parent Slice

- `draft_feature_plans/01_workflow_profile_yaml_family_and_structural_validation.md`

## Goal

Register `workflow_profile_definition` as a discoverable document family in the schema-loading surface.

## Implementation Subtasks

- register the family id and loader entry points in the schema registry
- wire packaged-resource discovery so builtin profile assets are found consistently
- add family-aware validation helpers that downstream tooling can call without special cases
