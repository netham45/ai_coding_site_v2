# Node Versioning And Supersession Decisions

## Summary

Phase F02 introduces durable node version history and explicit current-version selection without yet binding lifecycle or compiled workflow state to per-version rows.

## Decisions

- Added `node_versions` as immutable version-history rows for each logical node.
- Added `logical_node_current_versions` to distinguish `authoritative_node_version_id` from `latest_created_node_version_id`.
- Seeded `v1` automatically when a node is created through the daemon.
- Added explicit candidate creation and explicit cutover operations instead of silently superseding in place.
- Rejected superseding while the logical node has an active or paused run.
- Preserved logical-node-scoped lifecycle state for now rather than trying to retrofit historical per-version lifecycle rows early.

## Why

- The architecture requires candidate-versus-authoritative coexistence before cutover.
- A dedicated selector table keeps current views deterministic without requiring fragile derived queries.
- Rejecting active-run supersession is simpler and safer than silently pausing/cancelling runs before the richer run-orchestration phases exist.

## Deferred

- Binding lifecycle state, run history, prompts, and compiled workflows directly to version rows.
- Automatic pause/cancel conflict resolution during superseding rebuild.
- Candidate-failure classification and richer rebuild lineage views.
- Dependency evaluation and execution admission based on authoritative version selection.
