# Workflow Profile Subfeature Plan 06a: Required Role Coverage Calculation

## Parent Area

- `06 Child-Role Enforcement`

## Parent Slice

- `draft_feature_plans/03_profile_aware_layout_resolution_and_child_materialization.md`
- `draft_feature_plans/04_compiled_profile_context_and_brief_generation.md`

## Goal

Compute required child-role coverage from the selected profile and effective layout.

## Implementation Subtasks

- derive the required role set from profile obligations and effective layout metadata
- define handling for duplicates, optional roles, and role multiplicity
- produce a normalized coverage result that later enforcement and inspection surfaces can reuse
