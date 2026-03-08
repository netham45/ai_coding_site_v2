# Phase F02: Node Versioning And Supersession

## Goal

Implement durable node versioning rather than in-place mutation.

## Scope

- Database: logical-node identity, version identity, supersession lineage, rebuild mapping.
- CLI: supersedes/superseded-by inspection.
- Daemon: safe non-destructive version creation and supersession rules.
- YAML: bind compiled definitions to version identity, not mutable logical state.
- Prompts: keep prompt history aligned with version lineage.
- Tests: exhaustive version creation, stale-run handling, and historical reconstruction tests.
- Performance: benchmark lineage lookups and supersession-heavy queries.
- Notes: update versioning/cutover notes if old-run behavior changes.
