# Workflow Profile Subfeature Plan 08d: Persistence And Retrieval

## Parent Area

- `08 Brief Generation`

## Parent Slice

- `draft_feature_plans/04_compiled_profile_context_and_brief_generation.md`

## Goal

Persist workflow-brief payloads durably and retrieve them through stable read surfaces.

## Implementation Subtasks

- decide whether the brief is stored on compile records, node versions, or another durable table
- define retrieval behavior for current versus historical brief payloads
- ensure retrieval still works when prompt or compile assets later change
