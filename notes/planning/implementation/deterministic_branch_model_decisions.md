# Deterministic Branch Model Decisions

Date: 2026-03-08
Phase: `plan/features/12_F17_deterministic_branch_model.md`

## Decisions

1. Branch identity is now frozen to one canonical rule.
   The implementation uses `tier/<tier>/<kind>/<title-slug>__<logical_node_id_hex>/v<version_number>` so branch identity is derivable from durable node-version metadata and stays stable across inspection and audit paths.

2. Branch generation is aligned with durable version numbers.
   `branch_generation_number` currently equals `version_number`, and stale metadata is reported when that invariant is broken.

3. Seed/final commit anchors are explicit and immutable per version.
   Seed and final commit SHAs can now be recorded durably through daemon logic, are normalized to lowercase hex, and may not be rewritten to a different value once set.

4. Candidate rebuilds inherit the latest durable anchor.
   New candidate versions use the latest authoritative `final_commit_sha` as their seed when available; otherwise they inherit the prior seed anchor.

5. Git inspection is operator-facing before live git mutation is runtime-facing.
   The CLI now exposes branch, seed, and final inspection. Reset/merge/finalize command execution remains deferred until the rectification and merge phases land.

## Deliberate staging boundaries

- `active_head_sha` is still deferred because no live git/session orchestration layer owns that value yet.
- Recording `final_commit_sha` does not yet require the full validation/review/testing/docs pipeline; later runtime/git phases will tighten that guard.
- Branch metadata is validated and surfaced as `valid` or `stale`, but the current slice does not yet add a separate historical branch-event table.
