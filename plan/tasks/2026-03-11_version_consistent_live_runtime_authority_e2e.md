# Task: Version-Consistent Live Runtime Authority E2E

## Goal

Add real CLI/daemon/runtime proof that, after supersession or cutover, stale version-owned session and live-runtime state is not surfaced or rebound as the current node session/run for the newly authoritative version.

## Rationale

- Rationale: The bounded slice proved the version-binding logic inside lifecycle, admission, and supervision helpers, but the feature is not complete without a real runtime narrative through the daemon and CLI.
- Reason for existence: This task exists to move feature `85_F19_version_consistent_live_runtime_authority` from bounded proof toward the required real E2E layer.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`
- `plan/features/85_F19_version_consistent_live_runtime_authority.md`
- `plan/e2e_tests/05_e2e_git_rectification_and_cutover.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `notes/planning/implementation/live_rebuild_cutover_coordination_decisions.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`

## Scope

- Database: prove through real runtime behavior that the migrated `node_version_id` live-runtime columns are honored after authoritative version change.
- CLI: use real `node supersede`, `node version cutover`, `node cancel`, `node run start`, `session bind`, and `session list/show-current` commands.
- Daemon: prove that current-session and bind surfaces stay pinned to the authoritative version after cutover.
- Website: not affected in this batch.
- YAML: not affected in this batch.
- Prompts: not affected in this batch.
- Tests: add a real tmux-backed E2E narrative and update status tracking/logging accordingly.
- Performance: not a focus of this batch beyond ensuring the added real E2E stays at a single targeted narrative.
- Notes: document any newly discovered live-session surface leak if the E2E exposes one during implementation.

## Planned Changes

1. Extend an existing real regeneration/cutover or session-runtime E2E suite with a stale-version non-reuse scenario.
2. If the E2E exposes a remaining stale-session read leak, patch the affected daemon surface and add bounded coverage for it.
3. Update the checklist/dev log with the actual E2E status and any remaining gaps.

## Verification

Canonical verification commands for this task:

```bash
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_10_regenerate_and_rectify_real.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_session_records.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- a real daemon/CLI/tmux narrative proves old version-owned session/live runtime state is not surfaced as the current session after cutover
- if required, daemon session-read surfaces are corrected to respect authoritative version ownership
- the result is logged honestly as `e2e_passed` or `partial` depending on what the test actually proves
