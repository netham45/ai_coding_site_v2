# Conflict Detection And Resolution Decisions

## Scope

Phase `22_F20_conflict_detection_and_resolution` was implemented as durable merge-event and merge-conflict recording with explicit operator resolution and cutover blocking.

## Decisions

- `merge_events` and `merge_conflicts` were added as first-class durable tables instead of overloading generic failure history.
- The first implementation slice records conflicting merge attempts directly through daemon/CLI surfaces rather than waiting for the later automated rectification merge executor.
- `merge_conflicts.resolution_status` is bounded to `unresolved`, `resolved`, and `abandoned`.
- when a conflict belongs to the incremental parent-merge lane, `resolution_status = resolved` now means more than updating the conflict row: the parent repo must already be manually resolved and committed, and conflict resolution advances the affected incremental child merge row and parent lane to the resolved head
- Candidate-version cutover now rejects authority transfer while unresolved merge conflicts exist for that candidate parent version.
- The current cutover guard is local to the target candidate version; full required-scope conflict scanning remains deferred to the later rectification and lineage-cutover phases.

## Cross-System Impact

- Database: added `merge_events` and `merge_conflicts`.
- CLI: added `git merge-events show`, `git merge-conflicts show`, `git merge-conflicts record`, and `git merge-conflicts resolve`.
- Daemon: added durable conflict record/list/resolve APIs and the cutover guard for unresolved conflicts.
- YAML: no new schema family was required in this slice.
- Prompts: added a packaged merge-conflict pause guidance prompt for operator-facing conflict summaries.
