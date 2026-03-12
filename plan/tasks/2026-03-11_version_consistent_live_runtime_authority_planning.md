# Task: Version-Consistent Live Runtime Authority Planning

## Goal

Author an explicit feature plan for the narrow fix that makes shared live runtime authority rows version-consistent so stale versions cannot be restarted accidentally.

## Rationale

- Rationale: The repository is already substantially version-aware in runs and sessions, so the actual remaining gap is the shared logical-node live authority layer, not the entire execution architecture.
- Reason for existence: This task exists to capture that narrower fix precisely and avoid overcorrecting into a much larger redesign.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/05_F02_node_versioning_and_supersession.md`
- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/85_F19_version_consistent_live_runtime_authority.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `notes/planning/implementation/session_binding_and_resume_decisions.md`
- `notes/planning/implementation/regeneration_and_upstream_rectification_decisions.md`

## Scope

- Database: no schema change in this planning pass, but the feature plan must make the intended version-owned live-authority binding explicit.
- CLI: no direct CLI changes in this planning pass, but operator inspection implications must be called out.
- Daemon: define the narrow version-match checks and stale-runtime rejection points.
- YAML: not applicable.
- Prompts: no direct prompt work in this planning pass.
- Tests: define bounded, integration, and real E2E proof for the version-consistency fix.
- Performance: identify the expected lookup cost constraints.
- Notes: add the feature plan and record the planning work in the development log.

## Planned Changes

1. Add a feature plan under `plan/features/` for version-consistent live runtime authority.
2. Record the planning batch in `notes/logs/features/`.
3. Update the checklist backfill mapping for the new feature plan.
4. Run the authoritative document-family tests for the changed scope.

## Verification

Canonical verification commands for this task:

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_feature_plan_docs.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_feature_checklist_docs.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the narrow live-runtime version-consistency fix is captured in an authoritative feature plan
- checklist mapping and development log are updated for the new plan
- the documented verification commands are run and their results are recorded honestly
