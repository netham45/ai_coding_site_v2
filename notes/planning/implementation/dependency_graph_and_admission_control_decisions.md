# Dependency Graph And Admission Control Decisions

Date: 2026-03-08
Phase: `plan/features/11_F08_dependency_graph_and_admission_control.md`

## Decisions

1. Dependency edges attach to authoritative node versions, not logical nodes.
   The current implementation resolves `node_id -> authoritative node_version_id` at write and read time so admission always evaluates the current effective lineage rather than stale candidate versions.

2. First-pass dependency legality is intentionally narrow.
   Dependencies may currently target only siblings or direct children, and the required state vocabulary is currently limited to `COMPLETE`.

3. Blockers are persisted as a latest-snapshot surface.
   `node_dependency_blockers` stores the current explanation for invalid graphs, blocked waits, and impossible waits for the authoritative node version being checked. Historical blocker timelines remain deferred.

4. Run admission owns dependency enforcement.
   `node run start` now performs structural validation, dependency readiness evaluation, and active-run conflict checks before delegating to the lower-level authority mutation path.

5. Active-run conflict reasons take precedence over the generic lifecycle gate.
   If a node is already running, admission reports `active_run_conflict` and exposes the current run id instead of collapsing that case into `incompatible_lifecycle_state`.

## Deliberate staging boundaries

- YAML-driven declarative dependency authoring is still deferred; this slice adds durable/runtime enforcement and inspection surfaces first.
- Prompt changes are limited to existing blocked-state/runtime prompts consuming the new truth surface later; no new prompt family was required in this slice.
- Historical dependency-validation/audit tables remain deferred beyond the latest blocker snapshot.
- Scheduler-side automatic dependency creation for child materialization remains deferred to the later orchestration phases.

## Accepted extension direction

- The next sibling-dependency extension should keep authoritative-version-based dependency evaluation, but move sibling satisfaction from raw lifecycle `COMPLETE` truth toward merge-backed parent-state truth for cases where a dependent child must bootstrap from prerequisite sibling changes.
- The existing `node_dependency_blockers` latest-snapshot model should remain the primary blocker surface, expanding blocker kinds rather than introducing a parallel hidden dependency-readiness ledger.
- The current implementation slice now applies that rewrite to sibling edges that share a parent lineage: those dependencies become ready only after the prerequisite sibling has a durable successful incremental merge into the authoritative parent lineage.
- The current richer blocker kinds for that path are `blocked_on_incremental_merge`, `blocked_on_parent_refresh`, and `blocked_on_merge_conflict`.
- The daemon background auto-run pre-pass now owns the happy-path transition from `blocked_on_parent_refresh` to `ready` for inactive auto-run children by refreshing the child bootstrap at the current parent merge-lane head before the existing bind loop runs.
