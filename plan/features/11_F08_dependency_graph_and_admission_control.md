# Phase F08: Dependency Graph And Admission Control

## Goal

Implement valid dependency graphs, readiness checks, and run admission enforcement.

## Scope

- Database: dependency edges, dependency state, blocker read models.
- CLI: blockers, dependency status, and invalid-graph diagnostics.
- Daemon: dependency legality, readiness, impossible-wait detection, and admission.
- YAML: declarative dependency support in layouts and workflows.
- Prompts: blocked-state and startup-context prompts must reflect dependency truth.
- Tests: exhaustive valid/invalid graph, blocked, impossible-wait, and concurrency coverage.
- Performance: benchmark readiness classification and blocker queries.
- Notes: clarify dependency/child-summary startup context if implementation needs more explicit rules.
