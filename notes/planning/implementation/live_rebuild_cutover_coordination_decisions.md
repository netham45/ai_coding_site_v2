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
- the new live-coordination blockers currently include:
  - active or paused authoritative runs
  - active primary sessions on the authoritative run
  - unresolved durable merge conflicts
  - missing stable subtree/upstream rebuild completion for rebuild-backed candidates

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

- rebuild coordination still reports the current daemon-owned blocker set; it does not yet orchestrate automatic pause/cancel flows
- cutover readiness is still logical-node scoped because lifecycle state is still keyed by logical node id rather than by historical node version
- live git rebuild/finalize execution remains separate future work
