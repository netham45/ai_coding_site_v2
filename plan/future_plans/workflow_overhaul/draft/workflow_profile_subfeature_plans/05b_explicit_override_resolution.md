# Workflow Profile Subfeature Plan 05b: Explicit Override Resolution

## Parent Area

- `05 Materialization Layout Resolution`

## Parent Slice

- `draft_feature_plans/03_profile_aware_layout_resolution_and_child_materialization.md`

## Goal

Define how explicit layout overrides interact with selected workflow profiles.

## Implementation Subtasks

- accept explicit layout overrides at materialization time through daemon and CLI surfaces
- validate override compatibility against the selected profile and node kind
- surface clear blocked reasons when an override conflicts with required profile obligations
