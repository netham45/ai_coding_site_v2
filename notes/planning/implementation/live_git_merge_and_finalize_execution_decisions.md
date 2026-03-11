# Live Git Merge And Finalize Execution Decisions

## Summary

Feature `71_F11_live_git_merge_and_finalize_execution` is now implemented as a real daemon-owned git runtime path instead of a metadata-only staging layer.

## Decisions

### 1. Live repos remain per-version isolated

- each node version keeps its own working repository under `.runtime/git/node_versions/<version_id>`
- parent and child merge execution happens by fetching child final commits from those isolated repos into the parent repo
- this keeps replay and recovery bounded to durable node-version identity instead of sharing one mutable global checkout

### 2. Child bootstrap inherits parent ancestry by default

- `bootstrap_live_git_repo(...)` now defaults child repo bootstrap to `NodeVersion.parent_node_version_id`
- when a base version exists and its repo is already bootstrapped, the child repo is cloned from that base repo and checked out at the base seed commit on the child branch name
- this preserves true git ancestry, which is required for clean deterministic child merges

### 3. Final commits make children mergeable

- the reconcile layer now treats a recorded `final_commit_sha` as sufficient merge readiness unless the child is explicitly failed or paused
- this keeps the merge gate aligned with the real artifact the parent needs: a durable child final commit
- the previous requirement that lifecycle must also be `COMPLETE` was too strict for the shipped git runtime and caused the API merge path to silently skip finalized children

### 4. Empty live merges are rejected

- `execute_live_merge_children(...)` now raises a conflict when no mergeable child versions are provided
- the previous behavior incorrectly returned `status = merged` even when the reconcile layer had produced zero mergeable children

### 5. Finalize remains a real git commit step

- `git finalize-node` now requires a clean working tree and creates a real finalize commit with `git commit --allow-empty`
- the actual resulting commit SHA is written back to `node_versions.final_commit_sha`
- finalize failures and successful finalize operations are recorded through workflow-event audit

### 6. Incremental parent merge should extend the same live-git substrate

- the sibling-dependency incremental parent-merge path should reuse the same per-version isolated repos and durable `merge_events` / `merge_conflicts` audit model instead of inventing a second git-mutation substrate
- incremental merge order for that future path should be the actual daemon-applied completion order recorded durably per merge, not a separately precomputed deterministic sibling order
- the incremental merge lane should advance its own persisted parent-head pointer and should not overwrite `node_versions.final_commit_sha` during intermediate child merges; final parent finalize/reconcile remains a later explicit step
- pre-run child refresh may explicitly move a not-yet-started child version's `seed_commit_sha` forward to the current parent merge-lane head before re-bootstrap; this is the accepted refresh exception to the otherwise immutable child bootstrap seed story
- the daemon background child auto-start loop is now the happy-path owner of that pre-run refresh step; parent AI intervention remains reserved for conflict or later final reconcile paths

## Notes impact

The git, CLI, runtime, database, and flow-remediation notes were updated in the same slice so the repo no longer describes Flow 11 as staged-only.

## Testing

This slice was verified with:

- parser coverage for `git abort-merge`, `git finalize-node`, and `git status show`
- unit coverage for live repo bootstrap, clean merge/finalize, conflict/abort, and dirty finalize rejection
- daemon and CLI integration coverage for merge/finalize/status and conflict/abort
- Flow 11 contract coverage
- a performance guard for live merge plus finalize
