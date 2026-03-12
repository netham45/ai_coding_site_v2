# Task: Dependency-Aware Regeneration Scope Implementation

## Goal

Implement the first dependency-aware regeneration-scope runtime slice so candidate rebuilds persist explicit replay classifications, dependency-invalidated siblings stay non-stable until refresh/rematerialization, and cutover readiness blocks stale-baseline or replay-incomplete candidate lineages.

## Rationale

- Rationale: The current regeneration flow already finds reverse sibling dependents, but it still leaves too much of the replay contract implicit and can mark dependency-invalidated fresh candidates stable before they have actually refreshed or rematerialized.
- Reason for existence: This task exists to turn the updated F19 doctrine into concrete daemon/read-surface behavior before broader candidate replay and cutover work begins.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`
- `plan/features/83_F19_dependency_aware_regeneration_scope.md`
- `plan/features/84_F19_dependency_invalidated_node_fresh_rematerialization.md`
- `plan/features/85_F19_version_consistent_live_runtime_authority.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/pseudocode/modules/regenerate_node_and_descendants.md`
- `notes/pseudocode/modules/finalize_lineage_cutover.md`
- `notes/planning/implementation/regeneration_and_upstream_rectification_decisions.md`

## Scope

- Database: reuse `rebuild_events.details_json` and existing candidate version lineage to persist replay classifications and baseline references without introducing a new schema in this slice.
- CLI: no new command family in this slice, but existing rebuild-history and cutover-readiness surfaces must expose the new classification and blocker truth through their current payloads.
- Daemon: classify dependency-aware regeneration scope, avoid falsely marking dependency-invalidated fresh candidates stable, and add cutover blockers for replay incompleteness and authoritative-baseline drift.
- YAML: not applicable in this slice.
- Prompts: not applicable in this slice.
- Tests: add bounded and integration proof for replay classification visibility, non-stable invalidated candidates, and baseline-drift cutover blocking.
- Performance: keep scope classification and blocker lookup narrow to authoritative selector and rebuild-history queries.
- Notes: update the implementation doctrine and feature checklist/log surfaces to describe the new explicit replay classification and cutover blocking behavior.

## Planned Changes

1. Extend regeneration to persist explicit candidate scope and replay-classification details for regenerated, dependency-invalidated, and reused sibling nodes.
2. Stop treating dependency-invalidated fresh candidates as stable during the initial regeneration pass.
3. Extend cutover-readiness inspection to block replay-incomplete dependency-invalidated candidates and stale-baseline candidates whose authoritative lineage changed after rebuild start.
4. Update the relevant implementation note, checklist text, and development log.
5. Add targeted unit and integration coverage plus rerun the document-family checks for the changed authoritative docs.

## Verification

Canonical verification commands for this task:

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_regeneration.py tests/integration/test_node_versioning_flow.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q
git diff --check
```

## Exit Criteria

- rebuild history records explicit dependency-aware replay classifications instead of relying on implicit interpretation
- dependency-invalidated fresh candidates are not reported stable until later refresh/rematerialization work completes
- cutover-readiness reports replay-incomplete and authoritative-baseline-drift blockers for the affected candidate versions
- bounded and integration proof cover the implemented slice honestly
- notes, checklist text, and development log reflect the actual delivered scope
