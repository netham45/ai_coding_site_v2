# Workflow Profile Subfeature Plan 07e: Compile Failure Visibility

## Parent Area

- `07 Compile-Context Profile Freezing`

## Parent Slice

- `draft_feature_plans/04_compiled_profile_context_and_brief_generation.md`

## Goal

Make profile and layout compile failures durable and inspectable.

## Implementation Subtasks

- classify compile failures tied to profile selection, layout selection, or role obligations
- persist enough failure detail for later inspection without rerunning compile
- align CLI and daemon error reads so operators can see what part of compile failed
