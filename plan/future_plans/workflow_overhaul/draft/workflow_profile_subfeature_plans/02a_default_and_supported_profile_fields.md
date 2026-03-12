# Workflow Profile Subfeature Plan 02a: Default And Supported Profile Fields

## Parent Area

- `02 Node-Definition Extension`

## Parent Slice

- `draft_feature_plans/01_workflow_profile_yaml_family_and_structural_validation.md`
- `draft_feature_plans/02_profile_aware_startup_and_creation.md`

## Goal

Extend node definitions with explicit default and supported workflow-profile fields.

## Implementation Subtasks

- add `default_workflow_profile` and `supported_workflow_profiles` to the node-definition contract
- define which node kinds must declare these fields explicitly versus inheriting defaults
- document the invariants for parentless-capable kinds versus child-only kinds
