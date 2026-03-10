# Task: E2E Compile Variants And Diagnostics

## Goal

Add and run a real E2E suite for compile-stage diagnostics and compile variants, covering broken-policy failure capture, repaired recompilation, YAML override/policy inspection, and candidate/rebuild variant compilation through the real daemon and CLI path.

## Rationale

- Rationale: The phase-02 E2E plan and feature matrix already assign compile-stage schema validation, override resolution, rendering diagnostics, policy folding, and candidate/rebuild variants to a dedicated suite family.
- Reason for existence: This task exists to convert that compile-focused family from plan-only assignment into real executable proof without mixing in unrelated runtime remediation.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/e2e_tests/02_e2e_core_orchestration_and_cli_surface.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`
- `plan/features/03_F04_yaml_schema_system.md`
- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/09_F35_project_policy_extensibility.md`
- `plan/features/10_F06_override_and_merge_resolution.md`
- `plan/features/41_F03_variable_substitution_and_context_rendering.md`
- `plan/features/51_F03_source_discovery_and_loading_pipeline.md`
- `plan/features/52_F03_schema_validation_compile_stage.md`
- `plan/features/53_F03_override_resolution_compile_stage.md`
- `plan/features/54_F03_hook_expansion_and_policy_resolution_compile_stage.md`
- `plan/features/55_F03_rendering_and_compiled_payload_freeze_stage.md`
- `plan/features/56_F03_compiled_workflow_persistence_and_failure_diagnostics.md`
- `plan/features/63_F03_candidate_and_rebuild_compile_variants.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/contracts/persistence/compile_failure_persistence.md`

## Scope

- Database: prove durable compile-failure capture and subsequent compiled workflow persistence through the real runtime path.
- CLI: drive compile, compile-failures, source-discovery, schema-validation, override-resolution, hook-policy, rendering, YAML override/effective-policy/policy-impact/resolved, supersede, and regenerate through the real CLI subprocess path.
- Daemon: use the real daemon subprocess and real persistence-backed compile path.
- YAML: exercise project policy YAML, override YAML, and built-in YAML through actual load, validation, failure, repair, and compile behavior.
- Prompts: rely on the real prompt/runtime payload freeze as part of compile-stage rendering diagnostics.
- Tests: add one new real E2E suite file and run it directly.
- Performance: keep the suite bounded to one authoritative node plus one candidate and one rebuild candidate compile.
- Notes: update canonical command docs and maintain current task/development-log artifacts.

## Verification

- Compile diagnostics E2E suite: `python3 -m pytest tests/e2e/test_e2e_compile_variants_and_diagnostics.py -q`
- Document-schema targeted suite: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_verification_command_docs.py tests/unit/test_e2e_execution_policy_docs.py tests/unit/test_task_plan_docs.py -q`

## Exit Criteria

- `tests/e2e/test_e2e_compile_variants_and_diagnostics.py` exists and runs through the real daemon plus real CLI path.
- The suite proves one real compile failure, one repaired recompile, and one candidate plus rebuild compile variant.
- Canonical command docs mention the new targeted E2E command.
- Required task and development-log artifacts are current and pass the relevant document-schema tests.
