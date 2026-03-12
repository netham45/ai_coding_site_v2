# Workflow Profile Subfeature Plan 02b: Hierarchy Loader Support

## Parent Area

- `02 Node-Definition Extension`

## Parent Slice

- `draft_feature_plans/01_workflow_profile_yaml_family_and_structural_validation.md`
- `draft_feature_plans/02_profile_aware_startup_and_creation.md`

## Goal

Teach hierarchy loading to parse and expose node-definition profile metadata cleanly.

## Implementation Subtasks

- update hierarchy loaders to read normalized profile metadata from node definitions
- define the read model exposed to runtime consumers and inspection surfaces
- ensure loading failures remain attributable to node-definition assets instead of generic parse errors
