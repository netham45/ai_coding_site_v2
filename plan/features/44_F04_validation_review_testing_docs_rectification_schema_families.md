# Phase F04-S2: Verification, Docs, And Rectification Schema Families

## Goal

Author rigid schema families for the higher-order YAML artifacts instead of treating them as loosely implied extensions.

## Scope

- Database: persist schema-family and validation metadata where auditability requires it.
- CLI: expose schema validation and schema-family inspection for these families.
- Daemon: enforce schema validation before compilation or runtime use.
- YAML: author explicit rigid schemas for:
  - validation definitions
  - review definitions
  - testing definitions
  - documentation definitions
  - rectification definitions
- Prompts: validate schema-level prompt-bearing fields and prompt references in these families.
- Tests: exhaustively cover valid/invalid examples for every field and every family.
- Performance: benchmark validation cost across large definition packs.
- Notes: update schema and family-inventory notes when implementation freezes the exact field sets.
