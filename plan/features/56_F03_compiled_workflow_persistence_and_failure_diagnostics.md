# Phase F03-S7: Compiled Workflow Persistence And Failure Diagnostics

## Goal

Persist compiled workflows and compile failures cleanly as the final compiler stage.

## Rationale

- Rationale: The compiler is not finished until its outputs and failures are durably stored in a form the CLI and daemon can inspect later.
- Reason for existence: This phase exists to close the compile pipeline with persisted artifacts, rollback rules, and stage-specific diagnostics.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`: F03 is the parent compiler feature for this closing stage.
- `plan/features/06_F27_source_document_lineage.md`: F27 must be preserved in the persisted compiler outputs.
- `plan/features/55_F03_rendering_and_compiled_payload_freeze_stage.md`: F03-S6 produces the final artifacts this stage stores.
- `plan/features/57_F31_database_runtime_state_schema_family.md`: F31A consumes compiled workflow identities during execution.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/database/database_schema_spec_v2.md`
- `notes/contracts/persistence/compile_failure_persistence.md`
- `notes/pseudocode/00_compilation_plan.md`
- `notes/pseudocode/modules/compile_workflow.md`
- `notes/pseudocode/catalog/source_to_artifact_map.md`

## Scope

- Database: persist compiled workflows, compiled tasks/subtasks, compile-stage diagnostics, and compile-failure records.
- CLI: inspect compiled workflow artifacts and stage-specific failure diagnostics.
- Daemon: finalize compile output persistence and reject partial/invalid outputs.
- YAML: no new semantics beyond compiled artifact mapping.
- Prompts: ensure compiled prompt references remain inspectable in persisted output.
- Tests: exhaustively cover successful persistence, partial failure rollback, and stage-specific diagnostics.
- Performance: benchmark persistence overhead for large workflows.
- Notes: update compile-failure and traceability notes if diagnostics expand.
