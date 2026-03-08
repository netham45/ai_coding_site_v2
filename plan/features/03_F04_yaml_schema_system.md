# Phase F04: YAML Schema System

## Goal

Make every YAML family explicit, validated, and testable.

## Scope

- Database: persist schema-validation metadata where auditability requires it.
- CLI: YAML validate/show commands.
- Daemon: strict schema validation before compilation or mutation.
- YAML: author schemas for node, task, subtask, layout, validation, review, testing, docs, rectification, policy, and prompt-linked families.
- Prompts: validate prompt-family metadata and placeholder requirements.
- Tests: exhaustive valid/invalid cases for every schema family.
- Performance: benchmark validation over representative YAML sets.
- Notes: update schema notes when implementation exposes new families or constraints.
