# Workflow Profile Subfeature Plan 08e: Failure And Drift Rules

## Parent Area

- `08 Brief Generation`

## Parent Slice

- `draft_feature_plans/04_compiled_profile_context_and_brief_generation.md`

## Goal

Define how workflow-brief payloads behave across recompile, failure, and stale-state drift.

## Implementation Subtasks

- invalidate or replace stale brief payloads when profile or layout context changes
- define brief behavior when compile only partially succeeds
- keep brief freshness inspectable so sessions do not unknowingly reuse stale guidance
