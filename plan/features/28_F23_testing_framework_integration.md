# Phase F23: Testing Framework Integration

## Goal

Treat testing as a first-class quality gate with durable results and policy-aware retries.

## Rationale

- Rationale: For this repository, tests are part of correctness, so execution has to treat testing as a first-class gate instead of an optional afterthought.
- Reason for existence: This phase exists to connect project-defined test behavior to node completion, retries, and durable result history.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/25_F21_validation_framework.md`: F21 is the adjacent quality-gate model testing should align with.
- `plan/features/27_F26_hook_system.md`: F26 may inject testing behavior at lifecycle points.
- `plan/features/09_F35_project_policy_extensibility.md`: F35 makes testing policy project-extensible.
- `plan/features/13_F09_node_run_orchestration.md`: F09 enforces test-gate results before completion.

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

- Database: testing definitions, test runs, interpreted outcomes.
- CLI: test results and command-level outcome inspection.
- Daemon: authoritative test-gate execution and retry handling.
- YAML: testing definition family and test policy links.
- Prompts: testing-stage interpretation prompts where needed.
- Tests: exhaustive coverage for every testing gate, retry rule, and failure path.
- Performance: benchmark expensive test-gate orchestration paths.
- Notes: update testing notes if runtime/test-command boundaries change.
