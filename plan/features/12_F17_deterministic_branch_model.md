# Phase F17: Deterministic Branch Model

## Goal

Implement deterministic branch identity, seed/final tracking, and branch invariants.

## Scope

- Database: branch identity, seed commit, final commit, branch metadata.
- CLI: branch/seed/final inspection.
- Daemon: branch naming and branch-state invariant enforcement.
- YAML: policy only; no procedural git logic.
- Prompts: prompts may reference branch context but do not choose it.
- Tests: exhaustive branch naming, seed/final transition, and stale-branch coverage.
- Performance: benchmark branch metadata lookups.
- Notes: update branch naming notes if implementation forces changes.
