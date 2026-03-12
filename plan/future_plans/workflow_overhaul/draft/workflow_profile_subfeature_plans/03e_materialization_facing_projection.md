# Workflow Profile Subfeature Plan 03e: Materialization-Facing Projection

## Parent Area

- `03 Layout-Definition Extension`

## Parent Slice

- `draft_feature_plans/01_workflow_profile_yaml_family_and_structural_validation.md`
- `draft_feature_plans/03_profile_aware_layout_resolution_and_child_materialization.md`

## Goal

Project only the runtime-critical layout fields into materialization logic.

## Implementation Subtasks

- define the exact layout projection materialization receives at runtime
- separate authoring detail from runtime-critical role, profile, and compatibility data
- document how this projection remains inspectable without exposing raw layout internals everywhere
