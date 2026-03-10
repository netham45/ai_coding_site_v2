# Phase F02: Node Versioning And Supersession

## Goal

Implement durable node versioning rather than in-place mutation.

## Rationale

- Rationale: The architecture requires regeneration and historical lineage, which is incompatible with mutating a node in place and losing prior state.
- Reason for existence: This phase exists to give every meaningful rebuild or replacement a durable version history so supersession, rollback analysis, and audit trails remain coherent.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`: F01 defines the logical nodes that later acquire multiple versions.
- `plan/features/07_F03_immutable_workflow_compilation.md`: F03 binds compiled workflows to durable version identity.
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`: F19 relies on supersession during subtree regeneration and rebuild.
- `plan/features/35_F36_auditable_history_and_reproducibility.md`: F36 uses version lineage to reconstruct historical state.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/pseudocode/state_machines/lineage_authority.md`

## Scope

- Database: logical-node identity, version identity, supersession lineage, rebuild mapping.
- CLI: supersedes/superseded-by inspection.
- Daemon: safe non-destructive version creation and supersession rules.
- YAML: bind compiled definitions to version identity, not mutable logical state.
- Prompts: keep prompt history aligned with version lineage.
- Tests: exhaustive version creation, stale-run handling, and historical reconstruction tests.
- Performance: benchmark lineage lookups and supersession-heavy queries.
- Notes: update versioning/cutover notes if old-run behavior changes.
