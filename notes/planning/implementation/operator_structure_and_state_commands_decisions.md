## Phase

`plan/features/48_F11_operator_structure_and_state_commands.md`

## Decision

Close the remaining operator-structure/state command gaps at the CLI layer by projecting existing daemon reads instead of adding new daemon mutation or storage paths.

## Why

- The broader F11 implementation already delivered the daemon-backed summary, tree, blocker, dependency, sibling, pause-state, and current subtask reads.
- The remaining gap in this slice was command-family parity with the CLI spec: `task list`, `task current`, `subtask list`, plus the structure flags `tree show --full`, `node ancestors --to-root`, and `node children --versions`.
- Existing daemon reads already expose the necessary durable data:
  - current compiled workflow
  - durable lifecycle cursor
  - operator summary per node

## Implementation notes

- `task list --node <id>` now composes:
  - `GET /api/nodes/{id}/workflow/current`
  - `GET /api/nodes/{id}/lifecycle`
- `task current --node <id>` projects the current task from that same combined payload.
- `subtask list --node <id>` flattens the current compiled workflow and annotates each subtask with task identity plus `is_current`.
- `node children --versions` now enriches the child list with per-child operator summaries so authoritative/current version selectors are visible without a second manual lookup.
- `tree show --full` and `node ancestors --to-root` are currently explicit CLI flags over already-full daemon reads; they are accepted and reflected in the returned payload, but do not change daemon query shape yet.

## Deferred

- Run-scoped `task list --run <id>` and `subtask list --run <id>` remain deferred until the daemon exposes a dedicated run-scoped compiled-workflow read.
- If operator usage shows the child-summary enrichment is too slow on large sibling sets, move the `--versions` projection into a dedicated daemon endpoint or DB-backed summary view.
