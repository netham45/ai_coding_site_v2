# Task: YAML Schema And Field Rigidity Investigation

## Goal

Investigate the current YAML verification surface across built-in and project-facing YAML families, identify where schema validation and field-level rigidity checks are already present or missing, and produce the concrete implementation plan for closing those gaps.

## Rationale

- Rationale: The repository already validates YAML families and has some library-level tests, but it is not yet clear which YAML families have only coarse schema checks versus family-specific field rigidity checks.
- Reason for existence: This task exists to map the current proving surface before new YAML rigidity work begins, so later implementation can target real gaps rather than relying on assumptions.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`
- `plan/features/47_F10_ai_cli_progress_and_stage_transition_commands.md`
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`
- `plan/e2e_tests/02_e2e_core_orchestration_and_cli_surface.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/catalogs/inventory/default_yaml_library_plan.md`
- `notes/catalogs/audit/yaml_builtins_checklist.md`
- `notes/planning/implementation/ai_workflow_prompt_migration_phase3_protocol_hardening_targets_note.md`
- `notes/logs/reviews/2026-03-10_ai_workflow_prompt_migration_and_protocol_hardening.md`
- `AGENTS.md`

## Scope

- Database: review how YAML validation results are persisted and whether current tests verify durable schema-validation reporting adequately.
- CLI: inventory current YAML-facing validation and inspection commands and whether their tests cover all schema families and field-level expectations.
- Daemon: review daemon-side YAML validation, workflow compile-time schema reporting, and whether family-specific invariants are enforced beyond basic schema acceptance.
- YAML: inventory every active built-in YAML family and classify its current proving layer:
  - schema-only
  - library-presence only
  - compile/runtime-integrated
  - field-rigidity tested
- Prompts: include prompt-reference YAML because it defines prompt authority, but the main target is YAML document-family rigor rather than prompt prose.
- Tests: map current unit, integration, and E2E coverage for YAML families and identify missing family-specific rigidity checks.
- Performance: review whether broader YAML rigidity checks need any batching or family-level structure to avoid excessive repeated validation cost.
- Observability/auditability: verify that YAML validation failures and workflow schema-validation surfaces remain inspectable through the documented daemon/CLI boundaries.
- Notes: produce the investigation note and follow-on implementation plan for missing schema and field-rigidity tests.

## Plan

### Phase 1: YAML family inventory and current proving map

1. Enumerate all active built-in YAML families under `src/aicoding/resources/yaml/`.
2. Map each family to its current schema definition, validator model, and current test files.
3. Classify the current proving layer for each family:
   - presence only
   - schema validation only
   - family-library test
   - field-level rigidity test
   - compile/runtime-integrated test

### Phase 2: Gap taxonomy

1. Identify which YAML families are only covered by generic schema validation.
2. Identify which families have field-rich documents but no field-by-field rigidity assertions.
3. Identify which compile/runtime-sensitive families are missing integration proof through daemon or CLI boundaries.
4. Separate true gaps from intentionally shared family-level proving patterns.

### Phase 3: Rigid test strategy design

1. Define which YAML families should get:
   - stricter family-level unit tests
   - schema-negative tests
   - field-rigidity tests
   - integration tests through daemon/CLI compile/validation surfaces
2. Define how to avoid duplicate low-value tests while still defending every meaningful field and invariant.
3. Freeze the recommended test structure by family rather than one-off files.

### Phase 4: Follow-on implementation planning

1. Produce the investigation note summarizing the current coverage and gaps.
2. Create the follow-on task plan for implementing missing YAML rigidity tests.
3. Update any authoritative inventory/checklist notes if the investigation reveals stale coverage claims.

## Verification

- Review-time search commands:
  - `rg -n "yaml|schema|validate_yaml_document|test_.*yaml|test_.*schema" tests/unit tests/integration src/aicoding -S`
  - `find src/aicoding/resources/yaml -maxdepth 4 -type f | sort`
- Document-family checks:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- A dedicated investigation task plan exists for YAML schema and field-rigidity coverage.
- The investigation phases explicitly separate inventory, gap taxonomy, and follow-on implementation planning.
- The plan names the affected system boundaries instead of treating YAML as a standalone static asset.
- The canonical document-family verification command passes.
