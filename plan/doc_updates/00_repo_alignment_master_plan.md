# Phase DU-00: Repository Alignment Master Plan

## Goal

Bring the repository documentation and planning surface in line with the newer standards for:

- per-feature per-system checklist enforcement
- simulation-first / E2E-final verification progression
- explicit E2E coverage targets
- canonical verification commands
- normalized completion vocabulary
- current flow/traceability honesty

## Rationale

- Rationale: The project now has stronger standards than the documentation and tracking surface was originally written to enforce.
- Reason for existence: This phase exists to prevent the repository from claiming a stronger process than its notes, plans, and checklists actually support.

## Related Features

Read these implementation plans for context and interaction boundaries:

- `plan/update_tests/00_raise_existing_tests_to_doctrine_level.md`
- `plan/update_tests/01_batch_execution_groups.md`
- `plan/e2e_tests/00_e2e_feature_generation_strategy.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`
- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/audit/auditability_checklist.md`
- `notes/planning/implementation/full_real_end_to_end_flow_hardening_plan.md`

## Scope

- Database: document the status model and checklist expectations for DB-backed features and verification.
- CLI: normalize operator/AI CLI verification claims and command references across docs.
- Daemon: normalize daemon/runtime verification claims and real-boundary expectations across docs.
- YAML: ensure declarative asset docs distinguish schema presence from runtime-proven behavior.
- Prompts: ensure prompt existence, prompt runtime behavior, and prompt-history proof are tracked distinctly where needed.
- Notes: update repository-level and implementation-level notes to use the new checklist, status, and E2E language.
- Tests: the plans in this folder do not rewrite tests directly, but they define the documentation and tracking surfaces needed to govern that work.
- Performance: ensure documentation tracks performance-proof expectations where the doctrine now requires them.

## Deliverables

- a documentation alignment plan for the repo-level standards shift
- a feature-checklist and status backfill plan
- a status-vocabulary and command-reconciliation plan
- a flow/traceability/E2E status alignment plan
- a CI/E2E execution-policy and release-readiness plan

## Work Streams

1. Create and backfill the feature checklist system.
2. Normalize status vocabulary and canonical command references repo-wide.
3. Update flow, traceability, and audit docs to distinguish bounded proof from final E2E proof.
4. Define the CI/local/manual execution policy for bounded tests, integration tests, and required E2E tests.
5. Reconcile stale or scaffold-era docs that understate or misstate current repo scope.

## Exit Criteria

- the repository has an explicit checklist system for features and affected systems
- completion/status vocabulary is used consistently across notes and plans
- canonical commands are documented consistently across authoritative repo surfaces
- traceability docs can express bounded proof, E2E target, and E2E completion state
- release-readiness language matches the new doctrine

