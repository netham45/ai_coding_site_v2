# Database Provenance, Docs, And Audit Schema Family Decisions

## Phase

- `plan/features/59_F30_database_provenance_docs_audit_schema_family.md`

## Decision

- Keep this slice bounded to the missing database-side read structure for provenance and documentation instead of inventing another new persistence layer.
- Reuse the already-canonical append-only tables:
  - `documentation_outputs`
  - `code_entities`
  - `node_entity_changes`
  - `code_relations`
- Materialize current-state views over those histories:
  - `latest_documentation_outputs`
  - `latest_node_entity_changes`
  - `latest_code_relations`

## Why

- The daemon already treats these tables as the durable source of truth.
- The gap was query shape, not missing ownership.
- This matches the earlier runtime/session-history schema-family phases: add explicit views and composite indexes for hot inspection paths without changing the write contract.

## Query Surfaces Closed By This Slice

- docs inspection now has a direct latest-output view keyed by `(logical_node_id, scope, view_name)`
- per-version rationale inspection now has a direct latest-entity-change view keyed by `(node_version_id, entity_id)`
- per-version relation inspection now has a direct latest-relation view keyed by `(node_version_id, from_entity_id, to_entity_id, relation_type)`

## Deliberate Non-Goals

- no new provenance identity model
- no new docs build-event table
- no separate audit export table
- no attempt to collapse append-only provenance history into a mutable current-state table

## Performance Notes

- composite indexes were added for the ordered latest-row lookups the daemon already performs
- the docs path now has both `node_version`-ordered and `logical/scope/view`-ordered access paths
- provenance now has composite access paths for version/entity history, observed-name lookups, and relation traversal
