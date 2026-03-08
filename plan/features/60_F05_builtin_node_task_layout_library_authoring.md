# Phase F05A: Built-In Node, Task, Subtask, And Layout Library Authoring

## Goal

Author the built-in YAML families that define the default structural workflow surface.

## Scope

- Database: persist built-in identity and lineage metadata where needed for inspection.
- CLI: expose commands to list, inspect, and diff built-in structural YAML assets against overrides.
- Daemon: load structural built-ins deterministically and reject incomplete default packs.
- YAML: author built-in node definitions, task definitions, subtask definitions, layout definitions, and related variable-substitution-aware defaults.
- Prompts: bind each structural built-in to the correct prompt assets and placeholder contracts.
- Tests: exhaustively test schema validity, compileability, substitution behavior, and structural completeness of every built-in asset.
- Performance: benchmark built-in discovery and compilation cost for the structural library.
- Notes: keep built-in library notes synchronized with the actual authored structural assets.

## Exit Criteria

- the default structural YAML pack is complete enough to drive end-to-end workflow compilation.
