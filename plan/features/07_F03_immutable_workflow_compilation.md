# Phase F03: Immutable Workflow Compilation

## Goal

Compile mutable YAML and prompt references into immutable executable workflows.

## Rationale

- Rationale: Execution is only reproducible when it runs against frozen workflow artifacts rather than mutable YAML files that may change after a run starts.
- Reason for existence: This phase exists to establish the compile boundary that turns declarative inputs into stable execution state the daemon can trust.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`: F01 defines the structural inputs that compilation must preserve.
- `plan/features/05_F02_node_versioning_and_supersession.md`: F02 determines which node version a compiled workflow belongs to.
- `plan/features/03_F04_yaml_schema_system.md`: F04 validation gates compile inputs before later stages run.
- `plan/features/10_F06_override_and_merge_resolution.md`: F06 contributes deterministic source resolution before freeze.
- `plan/features/27_F26_hook_system.md`: F26 expands hook-driven workflow structure during compile.
- `plan/features/06_F27_source_document_lineage.md`: F27 captures the inputs and hashes behind each compile result.
- `plan/features/51_F03_source_discovery_and_loading_pipeline.md`: F03-S2 is the first compiler stage.
- `plan/features/52_F03_schema_validation_compile_stage.md`: F03-S3 performs schema rejection before later transforms.
- `plan/features/53_F03_override_resolution_compile_stage.md`: F03-S4 folds in override behavior.
- `plan/features/54_F03_hook_expansion_and_policy_resolution_compile_stage.md`: F03-S5 handles hooks and effective policy.
- `plan/features/55_F03_rendering_and_compiled_payload_freeze_stage.md`: F03-S6 freezes rendered payloads.
- `plan/features/56_F03_compiled_workflow_persistence_and_failure_diagnostics.md`: F03-S7 persists compiler outputs and failures.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/contracts/persistence/compile_failure_persistence.md`
- `notes/contracts/yaml/override_conflict_semantics.md`
- `notes/contracts/yaml/hook_expansion_algorithm.md`
- `notes/pseudocode/00_compilation_plan.md`

## Scope

- Database: compiled workflow/task/subtask tables and compile-failure persistence.
- CLI: compiled workflow and compile-failure inspection.
- Daemon: deterministic compile pipeline and persisted artifacts.
- YAML: source-to-compiled transformation for all execution families.
- Prompts: freeze prompt references into compiled workflow snapshots.
- Tests: exhaustive deterministic compile, failure-class, and bad-reference coverage.
- Performance: benchmark compile cost and repeated compile scenarios.
- Notes: update compile notes if implementation needs extra pipeline stages.
