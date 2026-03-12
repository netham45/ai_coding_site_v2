# Task: Dependency-Invalidated Manual Or Hybrid Rebuild Gate

## Goal

Prevent dependency-invalidated fresh restarts with prior manual or hybrid child trees from auto-transitioning to `READY` after parent refresh, and wire the first explicit rebuild/reconciliation path that can clear that blocked state on the fresh version itself.

## Rationale

- Rationale: Layout-authoritative dependency-invalidated restarts are now proved end to end, but manual or hybrid prior child trees needed both a hard block after refresh and an explicit fresh-version path to clear that block without reusing stale structure.
- Reason for existence: This task exists to close the unsafe gap where a fresh dependency-invalidated node with non-layout child authority could either look runnable too early or remain permanently blocked because the runtime lacked an explicit rebuild/reconciliation action on the fresh version.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/65_F04_layout_replacement_and_hybrid_reconciliation.md`
- `plan/features/78_F15_incremental_parent_merge_phase_04_dependent_child_parent_refresh.md`
- `plan/features/79_F09_incremental_parent_merge_phase_05_background_orchestration_and_autostart.md`
- `plan/features/84_F19_dependency_invalidated_node_fresh_rematerialization.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/planning/implementation/regeneration_and_upstream_rectification_decisions.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`

## Scope

- Database: inspect rebuild events and prior/current child authority to classify manual or hybrid fresh restarts.
- CLI: expose the blocked reason through existing dependency-status and child-reconciliation inspection surfaces, and allow explicit `preserve_manual` reconciliation on the fresh version.
- Daemon: keep manual or hybrid fresh restarts blocked after parent refresh instead of transitioning them to `READY`, then clear that gate only after explicit fresh-version rebuild or reconciliation.
- YAML: not applicable.
- Prompts: not applicable.
- Tests: add bounded proof for the new blocker and the no-auto-ready rule.
- Tests: extend bounded and integration proof so empty fresh versions can be reconciled through the daemon/API surface and manual child rebuild on the fresh version clears the blocker.
- Tests: extend the real incremental-parent-merge suite so the explicit fresh-version `preserve_manual` path is proved after grouped cutover and real prerequisite merge progression.
- Performance: keep the new blocker derivation bounded to current rebuild-event and prior-authority lookups for the authoritative node version only.
- Notes: record the new invariant and resulting limitation clearly.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_admission.py -q -k child_tree_rebuild_required
PYTHONPATH=src python3 -m pytest tests/unit/test_admission.py -q -k manual_restart
PYTHONPATH=src python3 -m pytest tests/unit/test_session_records.py -q -k manual_fresh_restart_child_blocked_after_refresh
PYTHONPATH=src python3 -m pytest tests/unit/test_materialization.py -q -k "dependency_invalidated or preserve_manual_for_empty"
PYTHONPATH=src python3 -m pytest tests/integration/test_node_versioning_flow.py -q -k empty_dependency_invalidated_manual_restart
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q -k "manual_restart_requires_explicit_reconcile or manual_restart_clears_after_fresh_manual_child_create"
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- dependency-invalidated fresh restarts with prior manual or hybrid child authority do not auto-transition to `READY` after parent refresh
- dependency-status reports an explicit blocker for the missing child-tree rebuild/reconciliation step
- bounded, daemon/API integration, and real incremental-parent-merge E2E tests defend the blocker plus both explicit fresh-version unblock paths: `preserve_manual` reconciliation and fresh manual child creation
- notes and development log are updated honestly
