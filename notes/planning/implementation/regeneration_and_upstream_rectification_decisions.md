# Regeneration And Upstream Rectification Decisions

## Scope

F19 is implemented as a staged durable rebuild pipeline rather than a live working-tree git executor.

## Decisions

1. Regeneration creates durable candidate node versions for the selected subtree and records rebuild history in `rebuild_events`.
2. Ordinary candidate versions clone version-scoped child edges, authority rows, and dependency edges so subtree rebuilds can be inspected before cutover, but dependency-invalidated sibling restarts are now the explicit exception: those fresh candidate versions start without cloned child structure and remain blocked until prerequisite sibling refresh/rematerialization work completes.
3. Shared live runtime rows remain keyed by logical node id, but they now bind to an explicit `node_version_id`; regeneration, cutover, admission, and supervision must ignore or rebind stale live rows instead of treating them as generic logical-node truth.
4. Workflow compilation now supports explicit candidate `node_version_id` targets so rebuilds do not need premature authority cutover.
5. Parent reconcile logic now has version-scoped inspection and execution paths so candidate parents can merge candidate children without reading back through authoritative selectors.
6. Cutover remains allowed for ordinary supersede candidates, but candidates that participate in rebuild history are blocked until at least one `stable` rebuild event exists for that candidate version.
7. Dependency-aware regeneration scope now records explicit replay classification in `rebuild_events.details_json`, including regenerated subtree members, dependency-invalidated fresh restarts, and reused authoritative siblings in the resolved scope summary.
8. Dependency-invalidated fresh restart candidates are not considered stable during the initial regeneration pass; they remain blocked pending parent refresh/rematerialization and cutover-readiness now reports that replay-incomplete state explicitly.
9. Dedicated real E2E coverage for the base regenerate/rectify path now lives in `tests/e2e/test_e2e_regeneration_and_upstream_rectification_real.py`, separating the standalone subtree-regenerate/upstream-rectify proof from the broader numbered Flow 10 narrative.
9. Upstream ancestor rectification must carry every dependency-invalidated fresh sibling candidate in the resolved scope, remap rebuilt parent child edges to those fresh candidates, and rebind each scoped child candidate's `parent_node_version_id` to the rebuilt ancestor candidate instead of leaving stale authoritative parent-version links in place.
10. After cutover, the background incremental-merge refresh loop now handles the first real follow-on for dependency-invalidated fresh restarts: when the fresh authoritative child is blocked on parent refresh, the daemon refreshes it from the updated parent head and auto-rematerializes layout-authoritative child structure from an empty tree before moving it back toward runnable state.
11. Grouped cutover may now return `ready_with_follow_on_replay` for rebuilt ancestors when the only remaining scope blockers are dependency-invalidated fresh-restart descendants waiting on post-cutover parent refresh/rematerialization; direct cutover of those descendants remains blocked.
12. The real follow-on rematerialization path must treat placeholder `manual` authority on dependency-invalidated fresh versions as stale rebuild carry-over: before layout rematerialization, the daemon resets that authority back to `layout_authoritative`, clears any stray carried child edges, and active child inspection surfaces must read authoritative `NodeChild` lineage rather than raw logical parent links.
13. If a dependency-invalidated fresh restart supersedes a version whose child authority was `manual` or `hybrid`, admission must report `child_tree_rebuild_required` after parent refresh and the background refresh loop must leave that node blocked instead of transitioning it to `READY`.
14. That manual/hybrid rebuild gate is now paired with an explicit daemon/API unblock path on the fresh version itself: new manual child creation on the fresh authoritative version or `preserve_manual` reconciliation on an empty fresh version clears the rebuild gate, while refresh alone never does.
15. Cutover-readiness now also blocks stale-baseline candidates whose `supersedes_node_version_id` no longer matches the current authoritative version for that logical node.
16. Rectification currently records deterministic synthetic seed/final commit anchors and merge history; actual `git reset`, branch checkout, and working-tree merge execution remain deferred.

## Follow-up Boundary

The next git-heavy phase should replace the synthetic seed/final commit generation with real branch checkout, reset-to-seed, merge, and conflict-materialization behavior while preserving the durable `rebuild_events` and `merge_events` audit model added here.
