# Phase F33: Optional Isolated Runtime Environments

## Goal

Provide optional bounded isolation for workloads that need environmental separation.

## Scope

- Database: environment requests, environment identity, and environment-failure context.
- CLI: environment selection and inspection if the feature is activated.
- Daemon: bounded environment orchestration without breaking recovery/scheduling correctness.
- YAML: environment policy declarations only.
- Prompts: add environment-specific prompts only if operator/session obligations materially change.
- Tests: exhaustive selection, environment failure, cleanup, and coexistence coverage if activated.
- Performance: benchmark environment startup and orchestration overhead if enabled.
- Notes: update environment notes if this feature moves from deferred to active.
