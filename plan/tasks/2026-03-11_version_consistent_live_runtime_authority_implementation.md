# Task: Version-Consistent Live Runtime Authority Implementation

## Goal

Implement the narrow runtime-authority fix so the shared live lifecycle and daemon-state rows stay bound to the correct node version and stale version-owned state cannot block, start, resume, or supervise work for the wrong version.

## Rationale

- Rationale: Durable runs and sessions are already mostly version-scoped, but the shared live authority rows still collapse state onto logical node identity alone.
- Reason for existence: This task exists to close that mismatch with a targeted schema/runtime update rather than a larger execution-architecture rewrite.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`
- `plan/features/84_F19_dependency_invalidated_node_fresh_rematerialization.md`
- `plan/features/85_F19_version_consistent_live_runtime_authority.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `notes/planning/implementation/regeneration_and_upstream_rectification_decisions.md`

## Scope

- Database: add `node_version_id` ownership to the shared live runtime tables and migrate existing rows onto current authoritative versions where possible.
- CLI: no new CLI command surface in this slice; existing inspection responses should expose the bound live version id once the daemon models carry it.
- Daemon: bind lifecycle and daemon-authority rows to concrete versions, reject stale live runtime rows in admission/readiness/supervision, and rebind those rows when runs or resets move live ownership to a new version.
- Website: not directly changed in this slice beyond daemon response fields becoming available.
- YAML: not applicable.
- Prompts: not applicable for this slice.
- Tests: add bounded proof for stale shared-runtime rejection and fresh-version rebinding; rely on migrated test schema to prove the database change is wired.
- Performance: keep checks to single-row or selector lookups on existing critical paths.
- Notes: update runtime and regeneration notes to state that live shared runtime authority is version-owned, not merely logical-node-owned.

## Planned Changes

1. Add an Alembic migration plus ORM model updates for `node_lifecycle_states.node_version_id` and `daemon_node_states.node_version_id`.
2. Extend lifecycle and authority snapshots/responses to include the bound live version id.
3. Bind or rebind shared runtime rows at the existing authority points: workflow compile/reset, run sync, regeneration reset, and cutover.
4. Add stale-version guards to readiness/admission/supervision so mismatched live rows are ignored or rejected instead of treated as current runnable state.
5. Add bounded tests covering stale authority rejection and fresh dependency-invalidated version rebinding.
6. Update the relevant notes, checklist status text, and development log with the actual scope proved by this slice.

## Verification

Canonical verification commands for this task:

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_node_lifecycle.py tests/unit/test_daemon_orchestration.py tests/unit/test_admission.py tests/unit/test_session_records.py tests/unit/test_regeneration.py -q
PYTHONPATH=src python3 -m pytest tests/integration/test_database_lifecycle.py tests/integration/test_node_versioning_flow.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- shared live runtime rows record the node version they currently govern
- stale version-owned lifecycle or daemon-state rows do not block or start authoritative work for a newer version
- dependency-invalidated fresh restart rebinds the live lifecycle row to the fresh version
- notes, checklist status, and development log reflect that this slice is bounded proof only until the real runtime E2E layer is added
