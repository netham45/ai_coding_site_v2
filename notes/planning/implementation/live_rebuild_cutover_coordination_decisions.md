# Live Rebuild Cutover Coordination Decisions

## Purpose

This note records the implementation boundary for feature `70_F19_live_rebuild_cutover_coordination`.

## What Landed

- rebuild coordination is now explicitly inspectable before mutation through:
  - `node rebuild-coordination --node <id> --scope subtree|upstream`
  - `GET /api/nodes/{id}/rebuild-coordination`
- candidate cutover readiness is now explicitly inspectable through:
  - `node version cutover-readiness --version <id>`
  - `GET /api/node-versions/{id}/cutover-readiness`
- blocked regenerate, rectify-upstream, and cutover attempts now write durable `rebuild_events` instead of only returning a `409`
- regenerate now cancels cancelable live subtree blockers before rebuild proceeds
- supersede can optionally request `cancel_active_subtree` so prompt-edit flows can cancel the authoritative subtree before creating the replacement candidate
- required cutover scope enumeration now returns rebuild-backed candidate versions in deterministic descendant-first order so replay and cutover-readiness do not inspect rebuilt ancestors before their required child candidates
- cutover-readiness now aggregates blockers across that enumerated scope and annotates which scoped candidate version triggered each blocker, so parent/upstream readiness matches the grouped authority-switch contract
- manual `node version cutover` now consumes that enumerated scope for rebuild-backed candidates, requiring every scoped candidate version to be cutover-ready and rebinding lifecycle plus daemon-state version ownership across the switched scope together
- grouped cutover now has one explicit follow-on exception: if the only remaining blockers are dependency-invalidated descendant `blocked_pending_parent_refresh` replay blockers plus the ancestor instability derived from them, the rebuilt ancestor scope may cut over with status `ready_with_follow_on_replay` so the authoritative background loop can finish refresh/rematerialization afterward
- the new live-coordination blockers currently include:
  - active or paused authoritative runs
  - active primary sessions on the authoritative run
  - unresolved durable merge conflicts
  - missing stable subtree/upstream rebuild completion for rebuild-backed candidates
- dedicated real E2E coverage now exists in `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py` for the two base live blocker narratives: upstream rectification blocked by an active authoritative run and candidate cutover blocked by an active authoritative tmux primary session

## Deliberate Boundary

This phase does not introduce real working-tree git execution.

The runtime now explains and audits live rebuild/cutover safety, but the actual live git reset/merge/finalize execution path remains deferred to the later git-runtime feature.

## Persistence Choice

No new table was added in this slice.

The implementation reuses:

- `rebuild_events` for blocked and allowed coordination audit
- `node_lifecycle_states` for current live run identity
- `sessions` for active primary session presence

This was sufficient because the missing behavior was not missing durable storage of the live state itself. It was missing explicit inspection and explicit audit of how that live state affects rebuild and cutover decisions.

## Current Limits

- rebuild coordination only auto-cancels daemon-owned live runtime blockers for regenerate and explicit supersede requests; unresolved merge conflicts and cutover-stability blockers still remain hard stops
- cutover readiness and current-session inspection still use one live row per logical node, but that live row is now bound to an explicit `node_version_id`; stale superseded session/runtime rows are ignored once authority moves
- live git rebuild/finalize execution remains separate future work, and the broader dedicated real rectification suite is still missing even though the narrower live blocker suite is now checked in
