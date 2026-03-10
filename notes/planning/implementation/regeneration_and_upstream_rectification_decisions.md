# Regeneration And Upstream Rectification Decisions

## Scope

F19 is implemented as a staged durable rebuild pipeline rather than a live working-tree git executor.

## Decisions

1. Regeneration creates durable candidate node versions for the selected subtree and records rebuild history in `rebuild_events`.
2. Candidate versions clone version-scoped child edges, authority rows, and dependency edges so subtree rebuilds can be inspected before cutover.
3. Workflow compilation now supports explicit candidate `node_version_id` targets so rebuilds do not need premature authority cutover.
4. Parent reconcile logic now has version-scoped inspection and execution paths so candidate parents can merge candidate children without reading back through authoritative selectors.
5. Cutover remains allowed for ordinary supersede candidates, but candidates that participate in rebuild history are blocked until at least one `stable` rebuild event exists for that candidate version.
6. Rectification currently records deterministic synthetic seed/final commit anchors and merge history; actual `git reset`, branch checkout, and working-tree merge execution remain deferred.

## Follow-up Boundary

The next git-heavy phase should replace the synthetic seed/final commit generation with real branch checkout, reset-to-seed, merge, and conflict-materialization behavior while preserving the durable `rebuild_events` and `merge_events` audit model added here.
