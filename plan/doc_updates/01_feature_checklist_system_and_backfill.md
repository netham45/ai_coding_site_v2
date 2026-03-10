# Phase DU-01: Feature Checklist System And Backfill

## Goal

Create the mandatory feature-checklist system required by the new standards and backfill it for the existing feature inventory.

## Rationale

- Rationale: The repository now requires per-feature status tracking across affected systems, but the current notes surface does not yet provide that canonical checklist layer.
- Reason for existence: This phase exists so feature status can no longer be implied from scattered plans, tests, or notes.

## Related Features

Read these implementation plans for context and interaction boundaries:

- `plan/features/README.md`
- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`
- `plan/features/35_F36_auditable_history_and_reproducibility.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`

## Scope

- Database: include explicit DB status tracking for each feature where applicable.
- CLI: include explicit CLI/API status tracking for each feature where applicable.
- Daemon: include explicit daemon/runtime status tracking for each feature where applicable.
- YAML: include explicit YAML/schema status tracking for each feature where applicable.
- Prompts: include explicit prompt/runtime-prompt status tracking for each feature where applicable.
- Notes: define where checklists live, what format they use, and how they are maintained.
- Tests: include separate bounded-test and E2E-test status tracking in the checklist model.
- Performance: include performance/resilience status where the feature family requires it.

## Work

- define one canonical checklist template
- define the allowed per-system statuses
- define the allowed overall feature statuses
- define how `not_applicable` is recorded
- define how bounded-test status and E2E status are tracked separately
- define where the checklist artifacts live
- backfill the checklist surface from `major_feature_inventory.md`, feature plans, and E2E matrix mappings
- ensure every existing feature has:
  - affected systems
  - per-system status
  - bounded test status
  - E2E target/status
  - overall status

## Suggested Outputs

- a checklist template note or plan
- a checklist directory or catalog for existing features
- a feature-to-checklist mapping if a separate index is needed

## Current DU-01 Outputs

- `notes/catalogs/checklists/README.md`
- `notes/catalogs/checklists/feature_checklist_standard.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `tests/unit/test_feature_checklist_docs.py`

## Canonical Verification Command

```bash
python3 -m pytest tests/unit/test_feature_checklist_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_notes_quickstart_docs.py
```

## Exit Criteria

- every existing feature has a current checklist entry
- every checklist distinguishes bounded-test status from E2E status
- overall status cannot exceed the weakest required system status
- the checklist layer is usable as the canonical feature-status surface
