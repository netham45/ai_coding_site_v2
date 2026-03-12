# Task: Dependency-Invalidated Follow-On Grouped Cutover

## Goal

Allow grouped rebuild-backed cutover to proceed when the only remaining scope blockers are dependency-invalidated fresh-restart descendants that must finish replay after authority moves to the rebuilt parent lineage.

## Rationale

- Rationale: Dependency-invalidated fresh restarts are intentionally childless and blocked pending parent refresh, but that made grouped parent cutover impossible even though the authoritative follow-on loop was already designed to finish the refresh/rematerialization work after cutover.
- Reason for existence: This task exists to bridge the mismatch between grouped cutover and authoritative follow-on replay without allowing arbitrary replay-incomplete candidates to cut over unsafely.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`
- `plan/features/84_F19_dependency_invalidated_node_fresh_rematerialization.md`
- `plan/features/85_F19_version_consistent_live_runtime_authority.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/pseudocode/modules/finalize_lineage_cutover.md`
- `notes/planning/implementation/live_rebuild_cutover_coordination_decisions.md`
- `notes/planning/implementation/regeneration_and_upstream_rectification_decisions.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`

## Scope

- Database: no schema change; rely on existing rebuild events, lineage selectors, and live runtime bindings.
- CLI: cutover-readiness responses may now return a grouped follow-on-ready status for rebuilt parents while direct dependency-invalidated child cutover stays blocked.
- Daemon: classify allowed follow-on replay blockers narrowly, permit grouped cutover for that case, and keep direct cutover blocked for the child itself.
- YAML: not applicable in this slice.
- Prompts: not applicable in this slice.
- Tests: add bounded and integration proof that grouped parent cutover can proceed with dependency-invalidated follow-on replay while direct child cutover remains blocked.
- Performance: keep the blocker classification bounded to the enumerated cutover scope.
- Notes: update cutover and regeneration decisions so the new grouped follow-on status is explicit and the remaining real E2E gap is stated honestly.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_regeneration.py -q
PYTHONPATH=src python3 -m pytest tests/integration/test_node_versioning_flow.py -q -k "cutover_readiness or dependency_invalidated or rectify_upstream_endpoint_remaps"
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_10_regenerate_and_rectify_real.py -q -k "dependency_invalidated or grouped_lineage_cutover"
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- grouped cutover-readiness reports `ready_with_follow_on_replay` when only dependency-invalidated descendant follow-on replay remains
- direct cutover of the dependency-invalidated child candidate itself still remains blocked
- grouped parent cutover succeeds through bounded and integration proving surfaces
- notes, checklist, and development log record that the broader real prerequisite-merge/rematerialization narrative is still pending
