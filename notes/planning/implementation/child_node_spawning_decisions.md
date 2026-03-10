# Child Node Spawning Decisions

## Scope

Phase `20_F15_child_node_spawning` was implemented as durable default-layout materialization for parent nodes with built-in layout support.

## Decisions

- Child materialization is keyed to the authoritative parent node version, not the logical node id alone.
- `node_children` stores `layout_child_id` explicitly so layout identity does not depend on mutable child titles.
- `parent_child_authority.authoritative_layout_hash` is the idempotency guard for default-layout materialization.
- Existing child edges plus a missing authoritative layout hash are treated as `reconciliation_required` to avoid duplicate child creation after partial work or interrupted runs.
- Child scheduling state is derived from durable dependency and lifecycle records instead of introducing a separate scheduling snapshot table in this phase.
- New child runs are not auto-started in this slice even when the child is `ready`; this phase stops at durable materialization plus readiness classification.

## Cross-System Impact

- Database: added `node_children` and `parent_child_authority`.
- CLI: added `node materialize-children` and `node child-materialization`.
- Daemon: added inspection/materialization APIs and layout validation, including cycle checks and ordinal validation.
- YAML: uses the authored built-in layout definitions already packaged in `system-yaml/layouts/`.
- Prompts: no new prompt family was needed; existing layout-generation prompts remain the authoring path while this phase consumes built-in layouts directly.
