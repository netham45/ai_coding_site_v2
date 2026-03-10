# Provider-Specific Session Recovery Surface Decisions

## Summary

Feature `67_F12_provider_specific_session_recovery_surface` adds an explicit provider-aware read and control layer on top of the existing provider-agnostic recovery model.

## Decisions

- Keep provider-agnostic recovery as the default and authoritative baseline.
- Add a provider-aware status surface instead of hiding provider restoration possibility inside generic recovery output.
- Add a provider-aware resume path that can rebind an existing durable primary session when:
  - the durable session has a persisted provider identity
  - the provider identity matches the active backend
  - the provider session still exists
  - the stored tmux session pointer is stale or missing
- Fall back to the existing provider-agnostic recovery path when those conditions are not met.

## New Surfaces

- `GET /api/nodes/{node_id}/recovery-provider-status`
- `POST /api/sessions/provider-resume`
- `ai-tool node recovery-provider-status --node <id>`
- `ai-tool session provider-resume --node <id>`

## Database

- No new migration was required.
- The existing `sessions.provider`, `sessions.provider_session_id`, and `session_events` families were sufficient for the first provider-aware slice.
- Provider-aware rebind attempts are audited through `provider_recovery_attempted` and `provider_recovery_rebound` event types.

## Why This Slice Is Bounded

- The current repo only has one concrete backend family, so provider-aware logic is intentionally conservative.
- This feature does not add arbitrary provider plugins or provider-owned workflow authority.
- It only makes direct session restoration explicit and testable when durable provider identity can safely support it.

## Remaining Boundary

- Provider-aware recovery still falls back to the provider-agnostic path for:
  - backend mismatch
  - missing provider identity
  - missing provider session
  - ambiguous or non-resumable run state
- Additional provider families can extend this model later without replacing the provider-agnostic classifier.
