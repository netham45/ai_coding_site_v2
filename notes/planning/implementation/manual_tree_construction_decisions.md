# Manual Tree Construction Decisions

## Scope

Phase `21_F16_manual_tree_construction` was implemented as durable manual child creation layered onto the same parent/child authority model used by layout materialization.

## Decisions

- Manual child creation now persists a `node_children` edge with `origin_type = manual` instead of relying on `hierarchy_nodes.parent_node_id` alone.
- The existing `node create --parent ...` path and the explicit `node child create ...` alias both use the same daemon-side manual tree logic.
- A parent with no prior authority record becomes `manual` on first manual child insertion.
- A `layout_authoritative` parent becomes `hybrid` as soon as a manual child is inserted.
- Entering `hybrid` clears the authoritative layout hash so subsequent layout materialization is forced into reconciliation instead of silent replacement.
- Manual remove, reorder, and replace flows are intentionally deferred; this slice closes the creation path first.

## Cross-System Impact

- Database: reuses `node_children` and `parent_child_authority` without requiring a new migration.
- CLI: adds `node child create` and strengthens the existing parented `node create` behavior.
- Daemon: parented manual node creation now updates structural authority metadata.
- YAML: no new schema family was required in this slice.
- Prompts: no new prompt assets were needed; reconciliation guidance remains a later slice.
