# Task: YAML Schema And Field Rigidity Implementation

## Goal

Implement the missing YAML schema-negative, family-library rigidity, and selected integration tests identified by the YAML schema and field-rigidity investigation.

## Rationale

- Rationale: The investigation established that the repository already has generic schema validation and several grouped library checks, but some YAML families still rely too heavily on indirect proof or coarse schema-only validation.
- Reason for existence: This task exists to land the missing rigidity tests in the right order, starting with the weakest families and preserving the code-vs-YAML boundary.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`
- `plan/features/47_F10_ai_cli_progress_and_stage_transition_commands.md`
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`
- `plan/e2e_tests/02_e2e_core_orchestration_and_cli_surface.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/planning/implementation/yaml_schema_and_field_rigidity_phase1_inventory_note.md`
- `notes/planning/implementation/yaml_schema_and_field_rigidity_phase2_gap_taxonomy_note.md`
- `notes/planning/implementation/yaml_schema_and_field_rigidity_phase3_test_strategy_note.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/catalogs/inventory/default_yaml_library_plan.md`
- `notes/catalogs/audit/yaml_builtins_checklist.md`
- `AGENTS.md`

## Scope

- Database: preserve durable YAML validation reporting and add tests only where the implementation changes the validation-reporting contract.
- CLI: retain the current `yaml validate` and library-inspection commands; add integration proof only where the rigidity work touches those user-facing surfaces.
- Daemon: retain current daemon validation and compile surfaces; add integration proof only for families whose YAML changes materially affect compile/runtime behavior.
- YAML: strengthen schema-negative and authored-library rigidity coverage for the families prioritized by the investigation.
- Prompts: prompt-reference YAML remains in scope only as a supporting YAML family; prompt prose is not the primary implementation target in this task.
- Tests: add family-level unit/library tests and selected integration tests without duplicating existing grouped-library proof.
- Performance: keep the new rigidity layer family-batched and avoid repeated whole-library rescans in many small tests.
- Observability/auditability: keep generic validation report and CLI/daemon inspection surfaces covered while adding stronger family-specific proof.
- Notes: update YAML specs, inventory/checklists, and the development log if the implementation reveals stale coverage claims or new family invariants.

## Plan

### Phase 1: Priority 1 family rigidity

1. Expand schema-negative validation tests for:
   - `rectification_definition`
   - `environment_policy_definition`
   - `validation_definition`
2. Add family-library rigidity tests for those same families.
3. Preserve existing grouped-library tests and extend them only where the family already belongs to that grouped surface.

### Phase 2: Priority 2 family rigidity

1. Expand schema-negative validation tests for:
   - `runtime_definition`
   - `project_policy_definition`
   - `override_definition`
2. Add family-level rigidity tests for the built-in or fixture-authored documents in those families.
3. Keep compile/runtime integration proof where those families already affect policy resolution or workflow compilation.

### Phase 3: Integration supplementation

1. Add or extend daemon/CLI/compile integration proof only where missing for:
   - environment-policy propagation/failure
   - project-policy validation and resolution
   - override validation and compile application
2. Avoid adding integration tests for families that are fully defended at the schema and family-library layers.

### Phase 4: Notes, logs, and status

1. Update YAML-spec and inventory/checklist notes if the implementation reveals stale claims or newly frozen family invariants.
2. Record the implementation batch in the development log.
3. Keep the distinction explicit between:
   - generic schema-validation surfaces
   - grouped library integrity surfaces
   - family-specific rigidity additions

## Verification

- Unit and family-library tests:
  - `python3 -m pytest tests/unit/test_yaml_schemas.py tests/unit/test_rectification_library.py tests/unit/test_environment_library.py tests/unit/test_validation_library.py tests/unit/test_runtime_library.py tests/unit/test_project_policy_library.py tests/unit/test_override_rigidity.py -q`
- Existing grouped-library tests after updates:
  - `python3 -m pytest tests/unit/test_structural_library.py tests/unit/test_quality_library.py tests/unit/test_operational_library.py tests/unit/test_subtask_library.py -q`
- Integration tests:
  - `python3 -m pytest tests/integration/test_yaml_validation.py tests/integration/test_default_yaml_library.py tests/integration/test_flow_yaml_contract_suite.py -q`
- Document-family checks:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- The weakest YAML families identified by the investigation have explicit schema-negative and family-library rigidity coverage.
- Runtime-sensitive YAML families with thin field coverage have the required family-level or integration supplementation.
- The new rigidity layer stays family-based rather than devolving into one-off file tests.
- The relevant notes and development log are current.
- The canonical verification commands for the implementation task pass.
