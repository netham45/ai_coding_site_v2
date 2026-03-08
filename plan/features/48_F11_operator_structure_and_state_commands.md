# Phase F11-S1: Operator Structure And State Commands

## Goal

Implement the operator CLI command family for structure, state, and blockers.

## Scope

- Database: create read models for node tree, lineage, state, blockers, and dependencies.
- CLI: implement:
  - node/tree/show commands
  - lineage and relationship inspection
  - blockers and dependency-status commands
  - current run/task/subtask state commands
- Daemon: serve or validate daemon-owned current-state reads where necessary.
- YAML: expose source/resolved structure references cleanly.
- Prompts: no major prompt changes beyond prompt-linked inspection references.
- Tests: exhaustively cover tree rendering, blocker reporting, stale-state handling, and edge-case lineage views.
- Performance: benchmark tree/state/blocker query latency.
- Notes: update introspection notes if additional structure/state views are needed.
