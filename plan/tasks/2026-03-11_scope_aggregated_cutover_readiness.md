# Task: Scope-Aggregated Cutover Readiness

## Goal

Align cutover-readiness inspection with rebuild-backed cutover scope so grouped subtree or upstream candidate lineages are blocked by any required scope member, not only by the requested candidate version in isolation.

## Rationale

- Rationale: Manual cutover already switches the enumerated candidate scope together, but readiness inspection was still evaluating one requested candidate version at a time.
- Reason for existence: This task exists to remove that mismatch so operator inspection, API responses, and cutover-blocked audit all report the same grouped readiness contract that the authority-switch path already enforces.

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
- `notes/catalogs/checklists/feature_checklist_backfill.md`

## Scope

- Database: no schema change; derive grouped readiness strictly from existing durable rebuild and lineage records.
- CLI: grouped cutover-readiness responses must surface blockers from any required scope member.
- Daemon: aggregate cutover blockers across `enumerate_required_cutover_scope(...)` and annotate which scoped candidate triggered each blocker.
- YAML: not applicable in this slice.
- Prompts: not applicable in this slice.
- Tests: add bounded and integration proof that parent/upstream readiness reflects dependency-invalidated sibling blockers.
- Performance: keep readiness aggregation bounded to enumerated scope members only.
- Notes: update cutover doctrine and feature status notes to match the grouped readiness contract that is now implemented.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_regeneration.py -q
PYTHONPATH=src python3 -m pytest tests/integration/test_node_versioning_flow.py -q -k "cutover_readiness or dependency_invalidated or rectify_upstream_endpoint_remaps"
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- cutover-readiness inspection evaluates the full required cutover scope for rebuild-backed candidates
- readiness blockers identify the specific scoped candidate version that caused the block
- daemon API coverage proves parent/upstream readiness reports dependency-invalidated sibling replay blockers
- notes, checklist, and development log are updated honestly for the implemented slice
