# Task: Rebuild Cutover Coordination Real E2E

## Goal

Add the dedicated real E2E suite for feature `70_F19_live_rebuild_cutover_coordination` so active-run rebuild blockers and active-primary-session cutover blockers are proven through the shipped CLI and daemon surfaces instead of only bounded and integration layers.

## Rationale

- Rationale: FC-15 already had bounded and integration proof for rebuild-coordination and cutover-readiness blockers, but the dedicated real suite named in the matrix was still missing.
- Reason for existence: This task exists to close the real runtime proving gap for live rebuild/cutover coordination without folding those blocker checks into unrelated flow narratives.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`
- `plan/features/85_F19_version_consistent_live_runtime_authority.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/planning/implementation/live_rebuild_cutover_coordination_decisions.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `plan/e2e_tests/05_e2e_git_rectification_and_cutover.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`

## Scope

- Database: rely on durable `rebuild_events`, authoritative lifecycle/runtime state, and session records written by the real daemon path.
- CLI: prove the shipped `node rebuild-coordination`, `node rectify-upstream`, `node version cutover-readiness`, `node version cutover`, and `node rebuild-history` commands on the real subprocess boundary.
- Daemon: prove that active authoritative runs block upstream rectification and that active authoritative primary sessions block candidate cutover.
- YAML: not affected in this slice.
- Prompts: not affected in this slice.
- Tests: add `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py` with the two dedicated live-blocker narratives.
- Performance: keep the suite focused on blocker inspection and blocked mutation outcomes rather than full replay/finalize progression.
- Notes: update the FC-15 checklist and live-coordination decision note to reflect the new dedicated real proof and the remaining gap honestly.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_rebuild_cutover_coordination_real.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the dedicated real E2E suite proves `node rebuild-coordination --scope upstream` reports `active_or_paused_run` and blocks real `node rectify-upstream`
- the same suite proves `node version cutover-readiness` reports both authoritative run and active primary-session blockers and that real `node version cutover` remains blocked while those sessions exist
- durable rebuild history records the blocked mutation events
- task/log/checklist/note updates reflect the new real proof and the remaining FC-15 gaps honestly
