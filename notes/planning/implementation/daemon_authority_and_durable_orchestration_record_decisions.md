# Daemon Authority And Durable Orchestration Record Decisions

## Purpose

Capture implementation choices made while completing `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`.

## Decisions

### Authority posture

- daemon mutation endpoints now perform durable writes before returning accepted responses
- legal mutation sequencing for this slice is enforced centrally in daemon orchestration helpers rather than inside CLI command code
- per-node mutation serialization uses PostgreSQL advisory transaction locks so concurrent start requests cannot create split-brain active runs for the same node

### Database posture

- this first authority slice persists daemon-owned runtime records in `daemon_node_states`, `daemon_mutation_events`, and the `daemon_active_node_runs` view
- the schema is intentionally keyed by external `node_id` strings for now because the full `node_versions` and `node_runs` schema families land in later feature slices
- this staging choice is transitional and should be replaced by the richer canonical runtime schema once those features are implemented

### CLI and daemon posture

- mutating node commands now return durable run/event identifiers from the daemon
- `node run show --node <id>` now has a real daemon-backed read path for the durable authority record
- lookup by durable run id remains deferred until the dedicated runtime schema and operator-introspection slices exist

### Test and performance posture

- coverage now includes legal and illegal authority mutations, daemon restart-safe readback, and concurrent start conflict handling
- migration and performance tests were updated so the durable-authority schema remains part of the tested baseline
