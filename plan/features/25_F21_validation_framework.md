# Phase F21: Validation Framework

## Goal

Make validation a first-class gate for stage completion and finalization.

## Rationale

- Rationale: Stage advancement and completion need objective checks that are modeled as system behavior, not informal expectations hidden in prompts.
- Reason for existence: This phase exists to make validation a durable, queryable gate with explicit failure semantics.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/03_F04_yaml_schema_system.md`: F04 defines the validation YAML families and task references.
- `plan/features/13_F09_node_run_orchestration.md`: F09 invokes validation as a stage-completion gate.
- `plan/features/28_F23_testing_framework_integration.md`: F23 is another quality-gate system that should stay behaviorally aligned.
- `plan/features/29_F24_user_gating_and_pause_flags.md`: F24 may pause or escalate based on validation outcomes.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`

## Scope

- Database: validation result persistence and history.
- CLI: validation inspection and failure details.
- Daemon: authoritative validation gating before cursor advancement/finalization.
- YAML: validation definitions and references from tasks/subtasks.
- Prompts: missed-step and missing-output prompts tied to actual validation failures.
- Tests: exhaustive coverage for every validation type and failure class.
- Performance: benchmark validation execution over common workflows.
- Notes: update validation notes when new check types are discovered.
