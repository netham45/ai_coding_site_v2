# Phase F33: Optional Isolated Runtime Environments

## Goal

Provide optional bounded isolation for workloads that need environmental separation.

## Rationale

- Rationale: Some workloads need environmental isolation, but the feature is explicitly optional and must not distort the core orchestration model.
- Reason for existence: This phase exists to bound isolation as an attachable capability with clear costs, lifecycle rules, and failure handling.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/19_F14_optional_pushed_child_sessions.md`: F14 is one context-isolation mechanism adjacent to full runtime isolation.
- `plan/features/20_F15_child_node_spawning.md`: F15 may be one of the workloads that later run inside optional isolated environments.
- `plan/features/09_F35_project_policy_extensibility.md`: F35 governs how environment policies are configured per project.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/contracts/runtime/runtime_environment_policy_note.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/planning/implementation/implementation_slicing_plan.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`

## Scope

- Database: environment requests, environment identity, and environment-failure context.
- CLI: environment selection and inspection if the feature is activated.
- Daemon: bounded environment orchestration without breaking recovery/scheduling correctness.
- YAML: environment policy declarations only.
- Prompts: add environment-specific prompts only if operator/session obligations materially change.
- Tests: exhaustive selection, environment failure, cleanup, and coexistence coverage if activated.
- Performance: benchmark environment startup and orchestration overhead if enabled.
- Notes: update environment notes if this feature moves from deferred to active.
