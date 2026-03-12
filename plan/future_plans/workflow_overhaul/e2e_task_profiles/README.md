# E2E Task Profiles

This directory documents the concrete `task.e2e.*` profile catalog implied by the current runtime flow inventory and real-E2E suite matrix.

These are future-plan assets only.

They are not active runtime YAML yet.

## Purpose

The starter profile bundle currently has one generic [task.e2e](../starter_workflow_profiles/task.e2e.yaml) profile.

That is useful as a base contract, but it is too coarse to drive real workflow decomposition once E2E work is treated as first-class task work.

This directory makes the next layer explicit:

- every canonical runtime journey that needs real proof can become its own `task.e2e.*` profile
- every specialized real-runtime suite family can also become its own `task.e2e.*` profile where the proving surface is materially different
- all of those concrete profiles inherit the same rigid leaf E2E chain from the `task.e2e` base

## Inheritance Model

All concrete E2E task profiles should inherit from the base `task.e2e` contract and only override:

- target runtime journey or suite
- required command family
- required evidence shape
- required repository updates
- special environment prerequisites
- special completion predicates where the runtime boundary is stricter than the base profile

They should not change the base leaf chain shape unless the runtime semantics truly differ.

## Catalog Split

- `canonical_flow_profiles.md`
  - one profile per canonical runtime flow
- `specialized_suite_profiles.md`
  - one profile per specialized real-E2E suite family that spans multiple features or runtime boundaries

## Composition Rule

Recommended future shape:

- base profile: `task.e2e`
- concrete flow profile examples:
  - `task.e2e.flow_01_create_top_level_node`
  - `task.e2e.flow_11_finalize_and_merge`
- concrete suite profile examples:
  - `task.e2e.quality_chain`
  - `task.e2e.incremental_parent_merge`

## Relationship To Existing Runtime Notes

Use this directory together with:

- `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `plan/e2e_tests/02_e2e_core_orchestration_and_cli_surface.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`
- `../starter_workflow_profiles/task.e2e.yaml`

## Intended Runtime Interpretation

The future compiler should be able to choose one of these concrete `task.e2e.*` profiles when a parent plan or phase decomposes real-proof work.

That would let E2E work be scheduled as explicit task nodes instead of an untyped generic “go run E2E” instruction.
