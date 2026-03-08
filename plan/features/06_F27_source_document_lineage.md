# Phase F27: Source Document Lineage

## Goal

Track every source YAML and related compile input used to create historical workflows.

## Scope

- Database: source docs, hashes, roles, and compile-input lineage.
- CLI: source and resolved YAML lineage inspection.
- Daemon: capture lineage during compile/recompile.
- YAML: make all compile-relevant inputs addressable and hashable.
- Prompts: bind prompt-template identity to source lineage where applicable.
- Tests: exhaustive lineage capture, hashing, and historical resolution tests.
- Performance: benchmark lineage persistence and lookup paths.
- Notes: update source-role taxonomy if missing categories appear.
