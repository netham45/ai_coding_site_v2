# Phase F07: Durable Node Lifecycle State

## Goal

Persist lifecycle and cursor state durably and enforce legal transitions.

## Scope

- Database: node/run lifecycle fields, cursor state, bounded vocabularies.
- CLI: lifecycle and current-state inspection surfaces.
- Daemon: legal transition enforcement and invariant checks.
- YAML: policy inputs only; no YAML-owned transition logic.
- Prompts: lifecycle-linked pause/failure hooks only.
- Tests: exhaustive legal/illegal transition coverage plus resume-safe cursor persistence.
- Performance: benchmark current-state lookups and transition writes.
- Notes: document lifecycle edge cases discovered during implementation.
