# Documentation

This tree contains the user-facing and operator-facing documentation surface for the live repository.

Use `docs/` for:

- onboarding and setup guidance for real users or operators
- supported workflow guides
- reference material for commands, configuration, and interfaces
- runbooks and troubleshooting procedures that operators are expected to follow

Boundary:

- `notes/` are governance, planning, specification, and traceability artifacts
- `docs/` are consumer-facing documentation artifacts
- `notes/scenarios/` is now a historical analysis and migration-pointer surface; it is not the primary user/operator documentation tree
- YAML `docs` assets define generated or packaged documentation outputs; they do not replace this documentation tree

Current entrypoints:

- `docs/user/getting-started.md`
- `docs/operator/first-live-run.md`
- `docs/operator/compile-and-yaml-inspection.md`
- `docs/operator/inspect-state-and-blockers.md`
- `docs/operator/tree-materialization-and-rebuild.md`
- `docs/operator/quality-provenance-and-finalize.md`
- `docs/reference/cli.md`
- `docs/reference/configuration.md`
- `docs/runbooks/pause-resume-recovery.md`
- `docs/runbooks/failure-escalation.md`
