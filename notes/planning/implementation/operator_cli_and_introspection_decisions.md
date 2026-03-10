# Operator CLI And Introspection Decisions

## Scope

This note records the implementation decisions for `plan/features/15_F11_operator_cli_and_introspection.md`.

## Decisions

- operator-facing structure/state commands are now daemon-backed for the current implemented runtime surfaces: `node show`, `tree show`, `node siblings`, `node pause-state`, and `node events`
- `node show` now resolves to an aggregated operator summary rather than only the raw hierarchy row, combining hierarchy identity, lifecycle state, current run pointer, current subtask pointer, authoritative/current version ids, and branch metadata
- `tree show` returns a flattened depth-aware subtree with live lifecycle/run status for each node so operators can inspect hierarchy and current state in one call
- `node events` currently reads from the compatibility `daemon_mutation_events` log, which is sufficient for current run-admission and pause/resume visibility until broader workflow/session event families land
- `workflow chain` now exposes run-aware state when an active run exists for the compiled workflow, including current/complete/pending/paused/failed derivation and latest-attempt metadata

## Deferred work

- dedicated workflow/session/merge/rebuild event families
- richer history and artifact commands for summaries, prompts, docs, and provenance
- run-id keyed `node run show --run <id>` lookup
- full operator history commands for rebuilds, cutovers, and merge diagnostics

## Notes impact

- CLI notes now distinguish the current operator-grade read surfaces from the still-deferred artifact/history families
- audit and database notes should continue treating `daemon_mutation_events` as a compatibility event surface rather than the final event model
