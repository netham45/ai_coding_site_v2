# Layout Replacement And Hybrid Reconciliation Decisions

## Summary

Feature `65_F04_layout_replacement_and_hybrid_reconciliation` adds the first explicit hybrid-reconciliation surface for parent child sets.

## Decisions

- Add a daemon-owned reconciliation inspection surface for parent child sets:
  - `GET /api/nodes/{node_id}/children/reconciliation`
  - CLI: `node child-reconciliation --node <id>`
- Add an explicit reconciliation mutation surface:
  - `POST /api/nodes/{node_id}/children/reconcile`
  - CLI: `node reconcile-children --node <id> --decision preserve_manual`
- Implement `preserve_manual` as the first concrete reconciliation decision:
  - convert all current child edges for the authoritative parent version to `origin_type = manual`
  - normalize their `layout_child_id` values to `manual-<child_node_version_id>`
  - set `parent_child_authority.authority_mode = manual`
  - clear `authoritative_layout_hash`
  - stamp `last_reconciled_at`
- Reuse the existing `parent_child_authority` and `node_children` records rather than adding a new reconciliation table in this slice.

## Why No Migration

This slice does not require a schema migration.

Reason:

- `node_children.origin_type` already captures whether a child edge is manual or layout-generated
- `parent_child_authority` already captures the parent child-set authority mode
- `parent_child_authority.last_reconciled_at` already exists for reconcile timestamps

## Remaining Boundary

- structural layout replacement is still bounded
- there is still no safe general-purpose child-set rewrite for:
  - removing layout children from the hierarchy tree
  - adopting a new layout that changes the child-id set
  - merging manual and layout structures into a new authoritative hybrid layout
- this slice closes the explicit reconciliation-choice gap for Flow 04, but not the full layout-replacement gap
