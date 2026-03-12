# Task: Regeneration And Upstream Rectification Real E2E

## Goal

Add the dedicated real E2E suite for feature `24_F19_regeneration_and_upstream_rectification` so subtree regeneration, upstream rectification, and dependency-invalidated sibling remap behavior are proven in a standalone real suite rather than only inside Flow 10 and bounded/integration layers.

## Rationale

- Rationale: The feature-to-suite matrix already mapped F19 regeneration/rectification to `tests/e2e/test_e2e_regeneration_and_upstream_rectification_real.py`, but that suite did not exist.
- Reason for existence: This task exists to make the dedicated real rectification proof explicit and traceable without relying on a flow-numbered suite as the only evidence.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`
- `plan/features/83_F19_dependency_aware_regeneration_scope.md`
- `plan/features/84_F19_dependency_invalidated_node_fresh_rematerialization.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/planning/implementation/regeneration_and_upstream_rectification_decisions.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `plan/e2e_tests/05_e2e_git_rectification_and_cutover.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`

## Scope

- Database: prove durable rebuild events, version lineage, and version-scoped child edges through real regenerate/rectify operations.
- CLI: prove the shipped `node regenerate`, `node rectify-upstream`, `node rebuild-history`, `node versions`, `node rebuild-coordination`, and `node version cutover-readiness` commands on the real subprocess boundary.
- Daemon: prove subtree regeneration, ancestor candidate rebuild, dependency-invalidated sibling candidate creation, and remap into the rebuilt parent candidate.
- YAML: not affected in this slice.
- Prompts: not affected in this slice.
- Tests: add `tests/e2e/test_e2e_regeneration_and_upstream_rectification_real.py` with the base round trip and the dependency-invalidated sibling remap narrative.
- Performance: keep the dedicated suite narrower than the full grouped-cutover and post-cutover follow-on narratives that already live elsewhere.
- Notes: update FC-15 status text and rectification decisions to reflect that the dedicated real rectification suite now exists, while broader full-tree regenerate/rebuild proof still remains separate.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_regeneration_and_upstream_rectification_real.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the dedicated real rectification suite proves the base subtree-regenerate/upstream-rectify round trip through real CLI and daemon paths
- the same suite proves dependency-invalidated sibling fresh restart candidates are childless and are remapped into the rebuilt parent candidate lineage
- FC-15 notes/checklist/log text reflects that the dedicated real rectification suite exists and that only the broader full-tree regenerate/rebuild narrative remains incomplete
