# Phase F03-S1: Candidate And Rebuild Compile Variants

## Goal

Promote candidate-version compile and rebuild compile into first-class, inspectable compile variants alongside the current authoritative compile path.

## Rationale

- Rationale: The current compiler surfaces are strong for authoritative workflow compilation, but regeneration, rectification, and candidate cutover paths still rely on narrower internal usage rather than a first-class compile contract.
- Reason for existence: This phase exists to make non-authoritative compile modes testable, inspectable, and safe instead of leaving them as implicit special cases.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`: F03 established immutable workflow persistence and baseline compile behavior.
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`: F19 already invokes candidate/rebuild compilation during regeneration.
- `plan/features/52_F03_schema_validation_compile_stage.md`: F03-S3 exposes one compile stage that must remain stable across compile modes.
- `plan/features/56_F03_compiled_workflow_persistence_and_failure_diagnostics.md`: F03-S7 owns durable compile failure handling that must extend to new compile variants.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/contracts/persistence/compile_failure_persistence.md`
- `notes/pseudocode/modules/compile_workflow.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`

## Scope

- Database: persist any compile-mode metadata or mode-specific pointers needed to distinguish authoritative, candidate, and rebuild compile results safely.
- CLI: add explicit compile-mode inspection and invocation surfaces where needed, without overloading the current authoritative-only assumptions.
- Daemon: make candidate-version compile and rebuild compile first-class runtime operations with consistent failure diagnostics and stage visibility.
- YAML: preserve compile-mode independence from YAML semantics; YAML remains declarative while compile mode stays daemon-owned.
- Prompts: ensure compile-stage guidance and any compile-failure prompts stay mode-aware where operator messaging changes.
- Tests: exhaustively cover authoritative, candidate, and rebuild compile modes, including failure, drift, and inspection parity.
- Performance: benchmark compile-stage reads and compile execution cost across all supported modes.
- Notes: update compile, lifecycle, and regeneration notes so compile variants are explicit rather than implied.
