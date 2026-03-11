# Task: YAML Schema And Field Rigidity Priority 3 Families

## Goal

Implement the deferred YAML rigidity work for the Priority 3 families identified by the investigation:

- `hook_definition`
- `runtime_policy_definition`
- `testing_definition`
- `docs_definition`

## Rationale

- Rationale: The earlier YAML rigidity task closed the Priority 1 and Priority 2 families plus the needed integration supplementation. The remaining deferred families already have meaningful grouped-library and runtime proof, but they still lack the richer family-level rigidity matrix called out by the investigation.
- Reason for existence: This task exists to strengthen authored-library and schema-negative coverage for the deferred higher-order YAML families without duplicating runtime behavior tests that are already proven elsewhere.

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

- Database: retain the current durable YAML validation reporting behavior; add DB-backed proof only where the deferred families already affect daemon/CLI/runtime resolution.
- CLI: retain current YAML/operator inspection commands and extend proof only where the deferred family already has a CLI-facing contract.
- Daemon: preserve existing compile/runtime behavior for hooks, runtime policies, testing, and docs; add integration supplementation only if family-level rigidity changes expose a real gap.
- YAML: add schema-negative and authored-library rigidity proof for the deferred families.
- Prompts: prompt-bearing YAML in these families remains in scope for binding integrity because prompt refs are part of the family contract.
- Tests: prefer family-batched unit/library proof and only reuse integration surfaces where they already exist.
- Performance: avoid repeated whole-library scans across many small tests.
- Observability/auditability: keep generic YAML validation and runtime inspection surfaces intact while adding stronger family-specific assertions.
- Notes: update YAML specs, inventories, and development logs if new invariants or already-implicit assumptions become explicit.

## Plan

### Phase 1: Gap confirmation and family inventory

1. Reconfirm the authored built-in and project-local inventory for:
   - hooks
   - runtime policies
   - testing definitions
   - docs definitions
2. Map the current proving layer for each family:
   - schema-negative coverage
   - grouped library coverage
   - prompt-binding coverage
   - runtime/daemon/CLI integration coverage
3. Freeze which gaps are still real versus already adequately defended.

### Phase 2: Schema-negative and family-library rigidity

1. Expand `tests/unit/test_yaml_schemas.py` only where the deferred families still lack targeted negative cases.
2. Add or extend family-library tests for:
   - `hook_definition`
   - `runtime_policy_definition`
   - `testing_definition`
   - `docs_definition`
3. Keep assertions invariant-based and family-batched rather than file-by-file.

### Phase 3: Integration supplementation only where still needed

1. Reuse existing daemon/CLI/runtime surfaces for:
   - hook selection/compilation
   - runtime policy resolution/effective policy inspection
   - testing runtime result routing
   - docs runtime build/list/show behavior
2. Add integration coverage only if the Phase 2 work reveals a genuine remaining family-level gap.

### Phase 4: Notes, logs, and status

1. Update YAML-spec and inventory/checklist notes if the task reveals stale claims or newly frozen invariants.
2. Record the work honestly in the development log.
3. Keep the verification commands and completion claim aligned with the actual proving layer reached.

## Verification

Operational note:

- Database-backed pytest commands in this task must be run sequentially against the shared test database. Do not kill unrelated pytest jobs; only run the DB-backed commands for this task when the shared test database is otherwise idle.

- Unit and family-library tests:
  - `python3 -m pytest tests/unit/test_yaml_schemas.py tests/unit/test_operational_library.py tests/unit/test_quality_library.py tests/unit/test_hook_library.py tests/unit/test_runtime_policy_library.py tests/unit/test_testing_library.py tests/unit/test_docs_library.py -q`
- Integration tests if still needed after Phase 2 review:
  - `python3 -m pytest tests/integration/test_yaml_validation.py tests/integration/test_default_yaml_library.py tests/integration/test_project_policy_flow.py tests/integration/test_override_flow.py tests/integration/test_daemon.py tests/integration/test_session_cli_and_daemon.py -k 'hook or runtime_policy or testing or docs' -q`
- Document-family checks:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- The deferred Priority 3 YAML families have explicit schema-negative and authored-library rigidity coverage where the investigation said they were still field-thin.
- Prompt-bearing deferred families retain binding integrity proof.
- Existing runtime/daemon/CLI proof remains sufficient or is supplemented only where a real gap exists.
- Notes and development logs are current.
- The canonical verification commands for the task pass for the reached scope.
