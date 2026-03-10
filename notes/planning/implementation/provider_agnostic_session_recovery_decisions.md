# Provider-Agnostic Session Recovery Decisions

## Scope

This note records the implementation boundary for `plan/features/17_F34_provider_agnostic_session_recovery.md`.

## Decisions

- Recovery is now classified from durable run state plus canonical `sessions` and current harness inspection, not from provider identity alone.
- No new migration was required in this phase. The existing `sessions`, `session_events`, and `node_run_state` records were sufficient to stage provider-agnostic recovery safely.
- `session resume --node <id>` is now the real recovery path. It returns a structured recovery result instead of only a raw session snapshot.
- `session recover --node <id>` was added as an explicit alias for the same recovery behavior.
- `node recovery-status --node <id>` was added so operators and automation can inspect the current recovery classification before acting.
- The staged classifier currently distinguishes `healthy`, `detached`, `stale_but_recoverable`, `lost`, `missing`, `ambiguous`, and `non_resumable`.
- When recovery is safe, the daemon reuses the existing session if possible and otherwise creates a replacement session from durable run state.
- When recovery is unsafe, the daemon now rejects recovery for non-resumable runs and pauses for user when duplicate active primary sessions make ownership ambiguous.

## Deferred Work

- Provider-specific resume handles are still treated as optional hints rather than a required recovery anchor.
- `session nudge --node <id>` remains deferred to the later idle-detection/nudge slice.
- Dedicated recovery-history tables remain deferred; `session_events` is the current audit surface.
