# Phase E2E-05: E2E Git, Rectification, Merge, And Cutover

## Goal

Create real E2E suites for branch identity, merge/finalize, conflict handling, rectification, rebuild, and cutover behavior using real git repositories and real runtime coordination.

## Rationale

- Rationale: Git and rebuild/cutover features are among the easiest areas to accidentally under-prove because bounded tests can verify durable records without proving the real working-tree and branch behavior.
- Reason for existence: This phase exists to ensure git and cutover features are exercised through real repos, real branch state, real merge operations, and real runtime coordination rules.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/12_F17_deterministic_branch_model.md`
- `plan/features/22_F20_conflict_detection_and_resolution.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/32_F30_code_provenance_and_rationale_mapping.md`
- `plan/features/35_F36_auditable_history_and_reproducibility.md`
- `plan/features/59_F30_database_provenance_docs_audit_schema_family.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`

## Required Notes

- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/contracts/parent_child/child_session_mergeback_contract.md`
- `notes/specs/provenance/provenance_identity_strategy.md`
- `notes/planning/implementation/full_real_end_to_end_flow_hardening_plan.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

## Scope

- Database: assert durable branch metadata, merge history, conflict records, rebuild events, cutover-readiness state, and audit outputs.
- CLI: drive git-related operator/runtime commands through the real CLI path.
- Daemon: run merge, finalize, rebuild, and cutover operations through the real daemon and real runtime blockers.
- YAML: prove any relevant rectification/rebuild/runtime policy behavior through actual execution paths where applicable.
- Prompts: exercise rectify/recovery prompts if the runtime uses them as part of the real flow.
- Notes: document canonical git/rebuild E2E commands and explicit environment requirements.
- Tests: use real git repositories, real working trees, and real branch transitions; do not replace the core behavior with durable staging only.
- Performance: keep repo setup bounded while still asserting real merge/cutover behavior.

## Proposed Suite Families

- `tests/e2e/test_e2e_branch_identity_and_history_real.py`
- `tests/e2e/test_e2e_live_git_merge_and_finalize_real.py`
- `tests/e2e/test_e2e_merge_conflict_and_resolution_real.py`
- `tests/e2e/test_e2e_regeneration_and_upstream_rectification_real.py`
- `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py`

## Exit Criteria

- git and rebuild/cutover features are proven through real repositories and real working-tree behavior
- durable records match actual git/runtime outcomes
- conflict, finalize, rebuild, and cutover paths are no longer considered verified by bounded staging proof alone
