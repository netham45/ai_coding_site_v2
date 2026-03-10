# Richer Child Scheduling And Blocker Explanation Decisions

## Summary

Feature `64_F08_F15_richer_child_scheduling_and_blocker_explanation` expands operator-facing child readiness explanation without introducing a second scheduling authority table.

## Decisions

- Keep dependency validation and readiness as the single daemon-owned scheduling authority.
- Broaden blocker explanation to include runtime-derived blockers in addition to dependency blockers:
  - `not_compiled`
  - `lifecycle_not_ready`
  - `pause_gate_active`
  - `already_running`
  - existing dependency blockers such as `blocked_on_dependency` and `impossible_wait`
- Continue persisting the current blocker snapshot in `node_dependency_blockers` even when the blocker is runtime-derived.
- Treat pause blockers as run-owned runtime state:
  - the canonical path is `node-runs/start` followed by `nodes/pause`
  - direct lifecycle inspection may expose `PAUSED_FOR_USER`, but pause-gate blockers are derived from the paused run state rather than from ad hoc lifecycle mutation alone
- Extend `node child-materialization` child rows with:
  - `scheduling_status`
  - `scheduling_reason`
  - `blockers`
- Extend `tree show` rows with:
  - `scheduling_status`
  - `blocker_count`

## Why No Migration

This slice does not require a schema migration.

Reason:

- `node_dependency_blockers` already stores the current replace-on-write blocker snapshot for a node version
- richer explanation is carried in `blocker_kind` plus `details_json`
- tree and materialization views can derive their scheduling summary from existing lifecycle, run, and blocker state

## Remaining Boundary

- automatic child run start is still deferred
- scheduler fairness and background scheduling loops are still deferred
- this phase improves explanation and inspectability, not autonomous child execution
