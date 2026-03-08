# Phase F06: Override And Merge Resolution

## Goal

Implement deterministic project-local override behavior across the YAML surface.

## Scope

- Database: override lineage and conflict records.
- CLI: override-chain and resolved-doc inspection.
- Daemon: deterministic override merge semantics.
- YAML: override schemas and field-level merge modes across families.
- Prompts: prompt override semantics with full auditability.
- Tests: exhaustive missing-target, ambiguity, conflict, and prompt-override coverage.
- Performance: benchmark large override sets and merge resolution.
- Notes: update override semantics notes if real fields require new merge rules.
