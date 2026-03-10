# Phase F17: Deterministic Branch Model

## Goal

Implement deterministic branch identity, seed/final tracking, and branch invariants.

## Rationale

- Rationale: Merge, rectification, and reproducibility all depend on stable branch identity and commit anchors across rebuilds.
- Reason for existence: This phase exists because git state has to be modeled as part of orchestration history, not left as an informal implementation detail.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/05_F02_node_versioning_and_supersession.md`: F02 ties branch identity to version lineage.
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`: F18 depends on deterministic branch identity and final commits.
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`: F19 rebuilds candidate lineages against this branch model.
- `plan/features/35_F36_auditable_history_and_reproducibility.md`: F36 uses stable branch metadata for reconstruction.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/pseudocode/state_machines/lineage_authority.md`

## Scope

- Database: branch identity, seed commit, final commit, branch metadata.
- CLI: branch/seed/final inspection.
- Daemon: branch naming and branch-state invariant enforcement.
- YAML: policy only; no procedural git logic.
- Prompts: prompts may reference branch context but do not choose it.
- Tests: exhaustive branch naming, seed/final transition, and stale-branch coverage.
- Performance: benchmark branch metadata lookups.
- Notes: update branch naming notes if implementation forces changes.
