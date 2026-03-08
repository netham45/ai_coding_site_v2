# Phase F03-S2: Source Discovery And Loading Pipeline

## Goal

Implement the first compiler stage: discovering and loading all compile inputs deterministically.

## Scope

- Database: persist source-discovery/load diagnostics and source input inventory as needed.
- CLI: inspect discovered source inputs and load failures.
- Daemon: discover built-ins, project-local extensions, overrides, prompts, and policy docs in deterministic order.
- YAML: define loadable families and source roots cleanly.
- Prompts: ensure prompt assets are discoverable through the same deterministic resource pipeline.
- Tests: exhaustively cover missing sources, duplicate/ambiguous sources, and deterministic load order.
- Performance: benchmark source discovery and load time.
- Notes: update compile/input notes if real source categories differ.
