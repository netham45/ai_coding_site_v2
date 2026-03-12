# Phase F19: Dependency-Invalidated Node Fresh Rematerialization

## Goal

Ensure that when a regenerated sibling invalidates a dependent sibling, the dependent sibling gets a fresh node version with no reused child tree and must rematerialize its children from scratch after refreshing against the updated parent state.

## Rationale

- Rationale: Reusing a dependent sibling's prior child tree after one of its prerequisite siblings is regenerated preserves stale structural and execution assumptions inside a lineage that should be rebuilt from updated parent truth.
- Reason for existence: This phase exists to make dependency invalidation reset the whole dependent node lineage cleanly instead of mixing regenerated prerequisite work with reused child versions from the dependent node's superseded version.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/11_F08_dependency_graph_and_admission_control.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/77_F08_incremental_parent_merge_phase_03_merge_backed_dependency_truth.md`
- `plan/features/78_F15_incremental_parent_merge_phase_04_dependent_child_parent_refresh.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/pseudocode/modules/regenerate_node_and_descendants.md`
- `notes/pseudocode/modules/rectify_node_from_seed.md`
- `notes/planning/implementation/regeneration_and_upstream_rectification_decisions.md`

## Scope

- Database: version-scoped child edges remain historical on superseded node versions, while dependency-invalidated fresh versions must start with no attached child tree and must record why they were reset structurally.
- CLI: lineage, rebuild-history, rebuild-coordination, cutover-readiness, dependency, and child-materialization inspection should show that a dependency-invalidated node received a fresh version with no reused children and now requires rematerialization.
- Daemon: detect reverse sibling dependency invalidation, create a fresh dependent node version without cloned child edges, block reuse of its old children, require parent refresh/bootstrap, and rerun materialization from an empty child set.
- Website: no browser-owned orchestration change is required, but daemon-backed rebuild and lineage views should eventually expose that the dependent node was structurally reset rather than incrementally reused.
- YAML: no new live coordination logic moves into YAML; dependency invalidation, fresh-version creation, and rematerialization remain daemon-owned behavior.
- Prompts: runtime context should eventually explain that the dependent node is restarting from a fresh structural lineage after sibling invalidation rather than resuming from reused child outputs.
- Tests: add bounded, integration, and real E2E proof that `A -> B` regeneration causes `B` to receive a childless fresh version, refresh from the updated parent state, and regenerate its child tree from nothing.
- Performance: reverse-dependency detection and rematerialization triggers must remain cheap enough for routine rebuild flows and avoid repeated full-tree rebuilds for unaffected nodes.
- Notes: update regeneration, rectification, child materialization, and cutover doctrine so dependency-invalidated nodes explicitly do not reuse their old child versions.

## Proposed Implementation Direction

1. Add a daemon-owned reverse-dependency invalidation pass that identifies sibling nodes invalidated by regenerated prerequisite siblings.
2. Introduce a fresh-supersede path for dependency-invalidated nodes:
   - create a new node version
   - do not clone `node_children`
   - do not clone version-scoped dependency edges that belong to old child structure
   - persist a rebuild/restart reason showing sibling dependency invalidation
   - keep the fresh dependent version in a blocked dependency-wait position rather than transitioning it to `READY`
3. Keep the old child tree attached only to the superseded node version for history and audit; it must not participate in the new dependent version's rebuild or reconcile flow.
4. After prerequisite sibling merge-up completes, refresh the dependent node's bootstrap against the updated parent head and rematerialize its children from an empty tree.
5. Only after that rematerialization and refreshed dependency check succeed may the dependent version move out of the blocked dependency-wait state; reset alone must not make it `READY`.
6. Add defensive guards so parent rectification and candidate reconcile reject any dependency-invalidated fresh version that still carries reused child edges from the superseded version.
7. Ensure operator inspection can distinguish:
   - ordinary candidate supersession with reusable structure
   - dependency-invalidated fresh restart with no reused structure
   - dependency-invalidated fresh restart still blocked on prerequisite sibling merge/refresh/rematerialization

## Runtime Clarifications

- A dependency-invalidated fresh version should be classified as `regenerate` or `blocked_pending_parent_refresh` by the candidate replay classifier; it must never remain in the `reuse` class.
- Fresh rematerialization should preserve the authoritative-baseline version the new candidate was built from so cutover-readiness can later reject stale candidates after baseline drift.
- Parent rectify and candidate replay should treat “fresh but not yet rematerialized” as replay-incomplete rather than as a structurally empty but acceptable child state.
- This phase should reuse the existing child materialization surfaces rather than inventing a separate rebuild-only child-tree bootstrap path.

## Verification Expectations

- Bounded proof:
  - regenerating `A` in `A -> B` creates a fresh `B` version
  - the fresh `B` version has no child edges even if old `B` had children
  - old `B` children remain only on the superseded `B` version for history
  - `B` stays blocked in the sibling-dependency wait position until parent refresh/bootstrap is updated after `A` merges
  - `B` child materialization reruns from an empty tree rather than reusing old child versions
  - resetting `B` does not by itself transition the fresh `B` version to `READY`
  - parent rectify/reconcile rejects stale-child reuse on dependency-invalidated fresh versions
- Integration proof:
  - daemon/API lineage, rebuild-history, rebuild-coordination, cutover-readiness, and child-materialization reads show the structural reset and later rematerialization clearly
- Real E2E proof:
  - a real `A -> B` flow with children under `B` proves that regenerating `A` causes `B` to restart cleanly, rematerialize after parent refresh, avoid any reuse of old `B` children, and remain cutover-blocking until replay-complete

## Exit Criteria

- dependency-invalidated nodes no longer reuse their prior child tree
- old children stay historical on the superseded version only and are not considered part of the fresh version
- the dependent node remains blocked after reset, then refreshes from updated parent truth and rematerializes children from nothing before becoming runnable
- notes and proving layers make this fresh-rematerialization rule explicit

## Current Progress Note

- Real Flow 10 now proves the reachable daemon/CLI path where dependency-invalidated sibling fresh candidates are carried into rebuilt parent candidates, refreshed against updated parent truth, and auto-rematerialized from an empty child tree when the authoritative path requires layout-owned child structure.
- `tests/e2e/test_e2e_incremental_parent_merge_real.py` now proves the missing real authoritative follow-on path for layout-authoritative child trees: grouped cutover makes the dependency-invalidated sibling authoritative, real prerequisite sibling completion advances the parent head, the daemon refreshes the blocked sibling against that head, clears stale carried child edges, restores layout authority, rematerializes a fresh child tree, and only then auto-starts the dependent side again.
- Bounded proof now also defends the non-layout side of that contract: if the superseded version carried `manual` or `hybrid` child authority, the fresh dependency-invalidated version reports `child_tree_rebuild_required` after parent refresh and does not auto-transition to `READY`.
- Bounded and integration proof now also cover the first explicit manual/hybrid follow-on: the fresh dependency-invalidated version exposes `preserve_manual` through the child-reconciliation surface even when its fresh tree is empty, and either explicit empty-tree `preserve_manual` or new manual child creation clears the rebuild gate on that fresh version.
- `tests/e2e/test_e2e_incremental_parent_merge_real.py` now also proves the real manual-authority follow-on for the explicit `preserve_manual` path: a prior-manual dependent sibling becomes a childless fresh authoritative version after grouped cutover and real merge progression, remains blocked on `child_tree_rebuild_required`, and only clears that blocker after real `node reconcile-children --decision preserve_manual` on the fresh version.
- `tests/e2e/test_e2e_incremental_parent_merge_real.py` now also proves the alternative real manual-authority unblock path via fresh-version manual child creation: after the same grouped cutover and real merge progression, creating a new manual child on the fresh authoritative version clears `child_tree_rebuild_required` without reusing any stale child lineage.
- Remaining gap: this feature’s manual/hybrid follow-on branches are now real-E2E-covered, but the broader FC-15 family still remains partial because the dedicated rectification and rebuild-cutover suites named in the feature matrix are not yet implemented.
