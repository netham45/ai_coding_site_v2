# Workflow Profile Subfeature Plan 06d: Child Profile Default Mapping

## Parent Area

- `06 Child-Role Enforcement`

## Parent Slice

- `draft_feature_plans/03_profile_aware_layout_resolution_and_child_materialization.md`
- `draft_feature_plans/04_compiled_profile_context_and_brief_generation.md`

## Goal

Map required child roles to legal child workflow profiles deterministically.

## Implementation Subtasks

- validate that each required role can resolve to a legal child profile
- define how role-to-profile defaults are stored in compile and materialization state
- expose the mapping in prompts and operator reads without making prompts the source of truth
