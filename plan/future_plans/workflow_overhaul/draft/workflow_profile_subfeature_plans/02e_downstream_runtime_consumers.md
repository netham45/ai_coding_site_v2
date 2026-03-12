# Workflow Profile Subfeature Plan 02e: Downstream Runtime Consumers

## Parent Area

- `02 Node-Definition Extension`

## Parent Slice

- `draft_feature_plans/01_workflow_profile_yaml_family_and_structural_validation.md`
- `draft_feature_plans/02_profile_aware_startup_and_creation.md`

## Goal

Identify and align the runtime paths that consume node-definition profile metadata.

## Implementation Subtasks

- map startup, compile, materialization, and inspection paths that need node-definition profile data
- define one normalized source so those paths do not re-interpret raw YAML differently
- document any transitional compatibility layer needed while legacy node-kind behavior still exists
