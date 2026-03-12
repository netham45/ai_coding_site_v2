# Workflow Profile Subfeature Plan 02d: Validation Rules

## Parent Area

- `02 Node-Definition Extension`

## Parent Slice

- `draft_feature_plans/01_workflow_profile_yaml_family_and_structural_validation.md`
- `draft_feature_plans/02_profile_aware_startup_and_creation.md`

## Goal

Validate node-definition profile metadata before runtime create and compile flows consume it.

## Implementation Subtasks

- enforce that default profiles belong to the supported profile set
- enforce that supported profiles apply to the same node kind as the node definition
- reject structurally illegal parentless combinations before startup reaches runtime mutation logic
