# Phase F11: Operator CLI And Introspection

## Goal

Provide operators with full visibility into state, history, and rationale.

## Scope

- Database: build read models for history and current-state inspection.
- CLI: node/tree/show, workflow, runs, prompts, summaries, sessions, blockers, merge, docs, provenance, and database-navigation commands.
- Daemon: serve or validate daemon-owned introspection surfaces.
- YAML: expose source versus resolved YAML.
- Prompts: prompt lineage inspection only.
- Tests: exhaustive command coverage for structure, history visibility, and edge cases.
- Performance: benchmark common inspection commands and tree rendering.
- Notes: update introspection notes if more surfaces prove necessary.
