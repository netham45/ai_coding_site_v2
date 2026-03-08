# Phase F03-S4: Override Resolution Compile Stage

## Goal

Implement override resolution as a separate compile stage with deterministic diagnostics.

## Scope

- Database: persist override-resolution diagnostics and resolved lineage details.
- CLI: inspect override-resolution outcomes and failures distinctly.
- Daemon: run deterministic override resolution after source loading/validation.
- YAML: resolve override documents across all supported families.
- Prompts: resolve prompt overrides without losing source identity.
- Tests: exhaustively cover missing-target, ambiguity, conflict, and resolved-success cases.
- Performance: benchmark override resolution at scale.
- Notes: update override and compile notes if stage semantics shift.
