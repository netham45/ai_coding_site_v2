# Child Merge And Reconcile Pipeline Decisions

## Scope landed in this phase

- The daemon now collects authoritative child results for a parent version from durable child edges, authoritative child selectors, lifecycle state, final commits, and latest summaries.
- Deterministic child merge order is now computed from sibling dependency edges, child ordinals, child-edge creation time, and logical child id.
- The daemon now exposes a staged child-merge command that records replayable `merge_events` and writes a durable `parent_reconcile_context` snapshot into the active run cursor.
- The packaged prompt `execution/reconcile_parent_after_merge.md` is now a first-class inspection surface through the daemon and CLI.

## Explicit staging boundary

- This phase does not yet shell out to live `git reset` or `git merge`.
- Instead, merge execution is metadata-backed: parent commit progression is represented by deterministic derived commit hashes in `merge_events`.
- This preserves auditability, replayability, and CLI/operator visibility without pretending the working tree is already under full daemon git control.

## Why this boundary was chosen

- The repository already had durable branch metadata, child authority, conflict records, and reconcile prompt assets.
- It did not yet have a safe live git-execution layer for reset, checkout, merge, and finalize.
- Implementing a fake working-tree mutator would have created misleading behavior and made the later git-runtime phases harder to reason about.

## Durable runtime consequence

- After `git merge-children --node <id>`, the active parent run now carries `parent_reconcile_context` in `node_run_state.execution_cursor_json`.
- `subtask context --node <id>` now includes that reconcile context so the active session can resume the reconcile stage without reconstructing child state from memory.

## Follow-up expectation

- Later git/runtime phases should replace the derived merge-head hashes with real working-tree-backed merge execution while preserving the same operator-facing `merge_events`, `child-results`, and `node reconcile` inspection surfaces.
