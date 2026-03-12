# Child Merge And Reconcile Pipeline Decisions

## Scope landed in this phase

- The daemon now collects authoritative child results for a parent version from durable child edges, authoritative child selectors, lifecycle state, final commits, and latest summaries.
- The authoritative live-parent reconcile path now reads actual applied child merge order from durable `merge_events` and incremental parent-merge history instead of synthesizing a second final-stage merge order.
- The daemon now exposes a staged child-merge command that records replayable `merge_events` and writes a durable `parent_reconcile_context` snapshot into the active run cursor.
- The packaged prompt `execution/reconcile_parent_after_merge.md` is now a first-class inspection surface through the daemon and CLI.

## Explicit staging boundary

- The authoritative live-parent reconcile path no longer records duplicate child merge events during final reconcile.
- For the current authoritative lineage, successful incremental merge execution is now the first and only child-to-parent merge point.
- Candidate-version rectification still retains its own replay path when rebuilding a non-authoritative lineage from seed.

## Why this boundary was chosen

- The repository now has a real daemon-owned incremental parent-merge lane for authoritative live children.
- Keeping final authoritative reconcile as a second merge engine would have double-merged the same child finals and made `merge_events`, `node child-results`, and `node reconcile` internally contradictory.
- Candidate-version rectification still needs a rebuild-time replay mechanism because those candidate lineages are not advanced by the authoritative live incremental-merge lane.

## Durable runtime consequence

- After `git merge-children --node <id>`, the active parent run now carries `parent_reconcile_context` in `node_run_state.execution_cursor_json`.
- `subtask context --node <id>` now includes that reconcile context so the active session can resume the reconcile stage without reconstructing child state from memory.
- `node child-results --node <id>` and `node reconcile --node <id>` now expose already-applied incremental merge order from durable merge history for the authoritative live parent lineage rather than a synthetic final-stage plan.
- The authoritative incremental merge lane is now seeded both by daemon-owned run terminal completion and by an explicit lifecycle transition to `COMPLETE` when the authoritative child version already has a recorded `final_commit_sha`. That keeps finalized no-run/manual hierarchy paths on the same merge-backed runtime contract as ordinary child runs.

## Newly explicit limitation

- The live authoritative reconcile path is now post-merge parent-local synthesis, but the candidate-version rectification path still replays child merges from seed when rebuilding a non-authoritative lineage.
- The remaining real E2E gap for this family is now candidate-lineage rectification and rebuild replay. The hierarchy-wide authoritative incremental merge plus final parent reconcile narrative now has passing real proof through the full-tree runtime suite.

## Immediate follow-up expectation

- Extend the real E2E layer so the authoritative live incremental-merge lane and later parent-local reconcile path are proven together through real runtime boundaries.

## Accepted design direction for the next implementation slice

- The incremental merge path should follow the repository's existing daemon-owned background-scan model rather than introducing a separate queue/claim worker abstraction.
- Child completion should make completed-unmerged child merge state durably discoverable, after which a background daemon pass can scan, take a per-parent advisory lock, and process at most one incremental merge step for that parent.
- Incremental merge ordering should be completion-driven at runtime. The daemon does not need a precomputed deterministic sibling merge sequence for this path; it must persist the actual applied incremental merge order instead.
- Existing operator surfaces such as `node blockers`, `node dependency-status`, `node child-results`, `node reconcile`, `git merge-events show`, and `git merge-conflicts show` should remain the primary inspection path for this feature unless they prove insufficient in practice.
- Pause, cancel, supersession, and cutover should stop future incremental merge progression without erasing already-written merge audit history for the affected lineage.
