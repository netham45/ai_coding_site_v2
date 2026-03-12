# Workflow Profile Subfeature Plan 06e: Non-Leaf Blocked Actions

## Parent Area

- `06 Child-Role Enforcement`

## Parent Slice

- `draft_feature_plans/03_profile_aware_layout_resolution_and_child_materialization.md`
- `draft_feature_plans/04_compiled_profile_context_and_brief_generation.md`

## Goal

Reject illegal non-leaf merge and completion attempts when required child structure is incomplete.

## Implementation Subtasks

- block merge and completion when child materialization or role coverage is incomplete
- return concrete blocked mutation responses such as `children_required_before_completion`
- keep blocked-reason data durable so later inspection and recovery can explain the refusal
