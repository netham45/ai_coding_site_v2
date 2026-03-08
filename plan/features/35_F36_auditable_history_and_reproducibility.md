# Phase F36: Auditable History And Reproducibility

## Goal

Make the full system reconstructible and inspectable without hidden critical state.

## Scope

- Database: verify critical state transitions are durably reconstructible.
- CLI: ensure audit and historical inspection surfaces are complete.
- Daemon: remove hidden-state assumptions and add missing durable emissions.
- YAML: preserve source and resolved YAML historically.
- Prompts: preserve prompt history and template identity reproducibly.
- Tests: exhaustive auditability and reconstruction coverage across create/run/pause/fail/recover/rebuild/inspect flows.
- Performance: benchmark critical history queries and reconstruction paths.
- Notes: drive updates from the auditability checklist until gaps are closed.
