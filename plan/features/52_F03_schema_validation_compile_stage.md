# Phase F03-S3: Schema Validation Compile Stage

## Goal

Implement schema validation as a dedicated compile stage with durable diagnostics.

## Scope

- Database: persist schema-validation failures and stage diagnostics.
- CLI: inspect schema-validation failures distinctly from later compile failures.
- Daemon: run schema validation after source load and before merge/expansion.
- YAML: validate every relevant family through the canonical schemas.
- Prompts: validate prompt-linked metadata at compile time.
- Tests: exhaustively cover schema-stage rejection across all major families.
- Performance: benchmark compile-time validation overhead.
- Notes: update compile-failure notes if schema-stage failure classes need refinement.
