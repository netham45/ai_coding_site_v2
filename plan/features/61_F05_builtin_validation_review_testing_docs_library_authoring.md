# Phase F05B: Built-In Validation, Review, Testing, And Docs Library Authoring

## Goal

Author the built-in YAML families that define default quality-gate and documentation behavior.

## Scope

- Database: persist built-in identity and result lineage metadata where needed.
- CLI: expose commands to inspect built-in quality-gate and docs definitions.
- Daemon: load quality-gate built-ins deterministically and enforce required gate ordering.
- YAML: author built-in validation, review, testing, and docs definitions, including failure handling and escalation references.
- Prompts: bind each quality-gate and docs built-in to its authored prompt templates and result contracts.
- Tests: exhaustively test schema validity, compileability, gate ordering, prompt bindings, and every expected success/failure contract.
- Performance: benchmark load and compile cost for the quality-gate YAML families.
- Notes: keep quality-gate/docs planning notes synchronized with the authored built-ins.

## Exit Criteria

- the default quality-gate YAML pack is complete, deterministic, and fully test-backed.
