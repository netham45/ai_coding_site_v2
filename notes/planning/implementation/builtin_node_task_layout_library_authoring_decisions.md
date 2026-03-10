# Built-In Node, Task, Subtask, And Layout Library Authoring Decisions

## Phase

- `plan/features/60_F05_builtin_node_task_layout_library_authoring.md`

## Decision

- Keep the active default runtime ladder unchanged for now.
- Author the remaining optional structural layouts as packaged built-ins.
- Add a structural-library integrity report and wire compilation to fail early when required built-in structural assets are missing or broken.

## Why

- The current default ladder is already exercised widely by the runtime and tests.
- Expanding node definitions or changing the active task ladder in this phase would silently change orchestration behavior far beyond library authoring.
- The immediate gap was structural completeness and inspectability of the built-in pack, not another runtime-behavior shift.

## Added In This Slice

- local CLI inspection for the built-in structural library manifest
- integrity checks for required built-in nodes, tasks, subtasks, and layouts
- authored optional layouts:
  - `layouts/manual_top_node.yaml`
  - `layouts/research_only_breakdown.yaml`
  - `layouts/replan_after_failure.yaml`
- a small benchmark-baseline increase for structural inspection and child materialization to account for the new compile-time integrity pass

## Deliberate Deferrals

- no new top-level `root` node kind yet
- no new `research_only` or `review_only` node kinds yet
- no silent expansion of the active default node `available_tasks` ladders
- no new prompt assets were required for this slice because the new layouts are declarative-only additions
