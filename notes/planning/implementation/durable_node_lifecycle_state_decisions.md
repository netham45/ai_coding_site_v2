# Durable Node Lifecycle State Decisions

## Summary

Phase F07 was implemented with a dedicated durable current-state table and daemon lifecycle service instead of trying to overload the earlier daemon authority record.

## Decisions

- Added `node_lifecycle_states` as the durable current-state and cursor surface for node lifecycle plus active run execution fields.
- Kept `daemon_node_states` and `daemon_mutation_events` as the daemon authority/audit surface for now.
- Normalized live daemon lifecycle values to the canonical vocabulary from the notes, including `RUNNING` and `PAUSED_FOR_USER`.
- Seeded hierarchy-created nodes at `DRAFT`.
- Preserved a temporary bootstrap path where daemon run admission can create a missing lifecycle row at `READY` for legacy non-versioned node ids used by early-phase authority commands and tests.

## Why

- The lifecycle spec already requires durable lifecycle and cursor state, but the repo does not yet have immutable compiled workflows or node version history.
- A dedicated table lets the daemon enforce legal transitions and persist resume-safe cursor fields now without pretending the fuller versioned execution model already exists.
- The bootstrap `READY` path avoids breaking the already-implemented daemon authority surface before the later compilation/versioning phases replace those assumptions.

## Deferred

- Replacing the legacy bootstrap `READY` path with strict compile-backed admission only.
- Moving from current-state-only lifecycle storage to a fuller node-version and run-history model.
- Tying lifecycle admission directly to compiled workflow, dependency readiness, and quality-gate ownership.

## Prompt/YAML Impact

- No new prompt assets were required in this slice.
- No YAML-owned lifecycle transition logic was added; lifecycle legality remains daemon-owned.
