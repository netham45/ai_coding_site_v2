# Phase F11-S2: Operator History And Artifact Commands

## Goal

Implement the operator CLI command family for history, artifacts, YAML, prompts, docs, and provenance.

## Scope

- Database: create read models for prompts, summaries, docs, provenance, rebuilds, merges, and workflow history.
- CLI: implement:
  - prompt and summary history commands
  - docs list/show/build inspection commands
  - provenance/entity/rationale commands
  - source/resolved YAML commands
  - merge/rebuild history commands
- Daemon: serve daemon-owned inspection where live state matters.
- YAML: expose source/resolved artifacts clearly.
- Prompts: prompt-lineage inspection commands must reflect actual prompt-template identity.
- Tests: exhaustively cover historical inspection, empty-history cases, and artifact lookup correctness.
- Performance: benchmark history and artifact query paths.
- Notes: update introspection and provenance/docs notes if new inspection surfaces are required.
