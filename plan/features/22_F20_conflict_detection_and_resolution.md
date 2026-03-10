# Phase F20: Conflict Detection And Resolution

## Goal

Persist merge conflicts durably and halt or resume safely through resolution.

## Rationale

- Rationale: Rectification and merge flows need a durable stop state when changes cannot be reconciled automatically.
- Reason for existence: This phase exists to keep conflicts visible, inspectable, and resumable instead of letting merge failures disappear into transient logs.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`: F18 is where many merge conflicts surface.
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`: F19 can produce conflicts during rebuild and cutover.
- `plan/features/12_F17_deterministic_branch_model.md`: F17 supplies branch identity needed to reason about conflict context.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/pseudocode/modules/finalize_lineage_cutover.md`

## Scope

- Database: conflict records, conflict resolution state, operator decisions.
- CLI: conflict inspection and resolution surfaces.
- Daemon: conflict detection during merge/rectification and safe halt behavior.
- YAML: conflict-handling policy inputs and optional conflict-resolution task hooks.
- Prompts: conflict pause/guidance prompts when operator action is required.
- Tests: exhaustive conflict detection, blocked progression, and resumed resolution coverage.
- Performance: benchmark conflict inspection paths.
- Notes: update conflict notes if extra states are needed.
