# Workflow Profile Subfeature Plan 01d: Cross-Reference Validation

## Parent Area

- `01 Schema Family Adoption`

## Parent Slice

- `draft_feature_plans/01_workflow_profile_yaml_family_and_structural_validation.md`

## Goal

Validate profile references against node kinds, layouts, and sibling profile ids.

## Implementation Subtasks

- enforce profile id uniqueness across builtin and loaded asset sets
- validate `applies_to_kind` and child references against known node kinds
- validate layout references, default child layouts, and related ids for referential integrity
