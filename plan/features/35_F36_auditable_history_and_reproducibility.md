# Phase F36: Auditable History And Reproducibility

## Goal

Make the full system reconstructible and inspectable without hidden critical state.

## Rationale

- Rationale: The architecture repeatedly treats auditability and reproducibility as correctness properties, not documentation niceties.
- Reason for existence: This phase exists to close any remaining hidden-state gaps so past behavior can be reconstructed from stored records alone.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/05_F02_node_versioning_and_supersession.md`: F02 preserves historical node lineage needed for reconstruction.
- `plan/features/07_F03_immutable_workflow_compilation.md`: F03 preserves compiled workflow state instead of relying on mutable sources.
- `plan/features/12_F17_deterministic_branch_model.md`: F17 anchors git history in reproducible branch metadata.
- `plan/features/06_F27_source_document_lineage.md`: F27 records the source inputs behind historical workflows.
- `plan/features/31_F28_prompt_history_and_summary_history.md`: F28 preserves the prompts and summaries an AI actually saw and emitted.
- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`: F31 removes hidden live state from the runtime model.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/audit/auditability_checklist.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`
- `notes/specs/prompts/prompt_library_plan.md`

## Scope

- Database: verify critical state transitions are durably reconstructible.
- CLI: ensure audit and historical inspection surfaces are complete.
- Daemon: remove hidden-state assumptions and add missing durable emissions.
- YAML: preserve source and resolved YAML historically.
- Prompts: preserve prompt history and template identity reproducibly.
- Tests: exhaustive auditability and reconstruction coverage across create/run/pause/fail/recover/rebuild/inspect flows.
- Performance: benchmark critical history queries and reconstruction paths.
- Notes: drive updates from the auditability checklist until gaps are closed.
