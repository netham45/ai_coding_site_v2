# Phase DU-03: Flow, Traceability, And E2E Status Alignment

## Goal

Update the flow, traceability, and audit tracking documents so they explicitly distinguish:

- simulated/bounded proof
- real E2E target assignment
- real E2E completion state

## Rationale

- Rationale: The repository has strong flow and traceability artifacts already, but they were not originally designed to track the newer E2E-first completion standard.
- Reason for existence: This phase exists to prevent the flow and traceability notes from overstating completion or hiding missing E2E coverage.

## Related Features

Read these implementation plans for context and interaction boundaries:

- `plan/e2e_tests/00_e2e_feature_generation_strategy.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`
- `plan/update_tests/00_raise_existing_tests_to_doctrine_level.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`
- `notes/catalogs/traceability/simulation_flow_union_inventory.md`
- `notes/planning/implementation/scenario_and_flow_pytest_plan.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`
- `notes/planning/implementation/full_real_end_to_end_flow_hardening_plan.md`

## Scope

- Database: reflect durable-state proof expectations in traceability language where needed.
- CLI: reflect real CLI/runtime proof expectations in flow and traceability docs.
- Daemon: reflect real daemon-boundary expectations in flow and traceability docs.
- YAML: distinguish schema/contract proof from runtime-proven declarative behavior.
- Prompts: distinguish prompt-asset presence from prompt-runtime and prompt-history proof where applicable.
- Notes: update flow coverage, traceability, and audit docs to track E2E targets and completion.
- Tests: align note language with the actual E2E rollout plans without pretending coverage exists before it does.
- Performance: note performance-proof dependencies only where these docs currently imply completed runtime behavior.

## Work

- extend or revise flow coverage docs to track:
  - bounded proof status
  - real E2E target
  - real E2E completion
- extend or revise the spec traceability matrix to include E2E coverage state or equivalent
- update simulation-flow inventory docs so simulation is clearly treated as planning and bounded proof, not final runtime proof
- reconcile partial/full labels in flow docs with the new doctrine
- ensure the feature-to-E2E matrix can be linked back into the note-level traceability surface

## Current DU-03 Outputs

- bounded-proof versus real-E2E summary table in `notes/catalogs/audit/flow_coverage_checklist.md`
- bounded-support clarification in `notes/planning/implementation/per_flow_gap_remediation_plan.md`
- simulation-versus-real-E2E clarification in `notes/catalogs/traceability/simulation_flow_union_inventory.md`
- target-assignment-only clarification in `plan/e2e_tests/06_e2e_feature_matrix.md`
- feature-family E2E backfill updates aligned to the documented Flow 01 through Flow 05 checkpoints in `notes/catalogs/checklists/feature_checklist_backfill.md`

## Canonical Verification Command

```bash
python3 -m pytest tests/unit/test_flow_e2e_alignment_docs.py tests/unit/test_verification_command_docs.py tests/unit/test_notes_quickstart_docs.py
```

## Exit Criteria

- flow docs no longer overstate completion
- traceability docs can represent the difference between bounded proof and real E2E proof
- every major feature/flow can be tracked to an E2E target or explicit partial/deferred state
