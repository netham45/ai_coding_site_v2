# Phase F04-S3: Runtime Policy And Prompt Schema Families

## Goal

Make runtime policy and prompt-linked YAML families explicit and rigid.

## Scope

- Database: persist enough schema/resource metadata for auditability.
- CLI: inspect runtime-policy and prompt-linked YAML sources and validation results.
- Daemon: enforce validation before runtime policy or prompt references are accepted.
- YAML: author explicit schemas for:
  - runtime/session policy definitions
  - prompt-linked references and placeholders
  - variable/render metadata where applicable
- Prompts: freeze prompt placeholder and metadata rules at schema level.
- Tests: exhaustively cover allowed/illegal policy fields, placeholder declarations, and prompt-link constraints.
- Performance: benchmark policy and prompt-schema validation cost.
- Notes: update runtime-policy and prompt-library notes when the schema model is finalized.
