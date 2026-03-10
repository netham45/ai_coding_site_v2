# Phase F22: Review Framework

## Goal

Support review stages as typed quality gates with durable results.

## Rationale

- Rationale: Not every quality gate is a mechanical validation; the architecture also calls for typed review stages with explicit outcomes.
- Reason for existence: This phase exists to keep review behavior structured, durable, and enforceable instead of burying it inside free-form task execution.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/03_F04_yaml_schema_system.md`: F04 constrains how review definitions are expressed.
- `plan/features/13_F09_node_run_orchestration.md`: F09 routes execution into review stages and outcomes.
- `plan/features/25_F21_validation_framework.md`: F21 is an adjacent gate that should stay consistent with review semantics.
- `plan/features/29_F24_user_gating_and_pause_flags.md`: F24 may be triggered by review outcomes that require human approval.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/planning/expansion/review_testing_docs_yaml_plan.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`

## Scope

- Database: review definitions, results, findings, outcomes.
- CLI: review result and revise/fail inspection.
- Daemon: review gating and routing after pass/revise/fail.
- YAML: review definition family and task references.
- Prompts: layout-review and node-review prompt assets.
- Tests: exhaustive pass, revise, fail, and user-gated review coverage.
- Performance: benchmark review result retrieval and repeated review stages.
- Notes: update review notes if additional scopes or actions are required.
