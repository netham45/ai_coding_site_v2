# Phase F03-S4: Override Resolution Compile Stage

## Goal

Implement override resolution as a separate compile stage with deterministic diagnostics.

## Rationale

- Rationale: Override folding is a distinct transformation with its own lineage and error cases, so it should not be hidden inside generic compilation.
- Reason for existence: This phase exists to make override behavior independently diagnosable and reproducible.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`: F03 is the parent compiler feature for this stage.
- `plan/features/10_F06_override_and_merge_resolution.md`: F06 is the feature this stage operationalizes.
- `plan/features/51_F03_source_discovery_and_loading_pipeline.md`: F03-S2 establishes the source set this stage resolves.
- `plan/features/52_F03_schema_validation_compile_stage.md`: F03-S3 must run first so only valid sources enter override resolution.
- `plan/features/54_F03_hook_expansion_and_policy_resolution_compile_stage.md`: F03-S5 consumes the resolved documents from this stage.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/contracts/yaml/override_conflict_semantics.md`
- `notes/contracts/yaml/override_versioning_note.md`
- `notes/pseudocode/00_compilation_plan.md`
- `notes/pseudocode/modules/compile_workflow.md`

## Scope

- Database: persist override-resolution diagnostics and resolved lineage details.
- CLI: inspect override-resolution outcomes and failures distinctly.
- Daemon: run deterministic override resolution after source loading/validation.
- YAML: resolve override documents across all supported families.
- Prompts: resolve prompt overrides without losing source identity.
- Tests: exhaustively cover missing-target, ambiguity, conflict, and resolved-success cases.
- Performance: benchmark override resolution at scale.
- Notes: update override and compile notes if stage semantics shift.
