# Module: `materialize_layout_children(...)`

## Purpose

Convert a parent's authoritative layout into durable child node versions and dependency edges.

This module owns structural creation. It does not decide which children start running immediately after creation.

---

## Source notes

Primary:

- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/contracts/runtime/invalid_dependency_graph_handling.md`

Supporting:

- `notes/contracts/parent_child/manual_vs_auto_tree_interaction.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/catalogs/vocabulary/state_value_catalog.md`

---

## Inputs

- `parent_node_version_id`
- resolved authoritative layout definition
- parent node kind and tier
- parent/child constraint rules
- current child-set authority mode
- project policy affecting auto-run and mixed-mode behavior

---

## Required state

- parent node version exists and is authoritative for this structure update
- layout hash or equivalent version is available
- existing child set and dependency edges are queryable
- child origin and authority mode are queryable or derivable

---

## Outputs

On success:

- durable child node versions
- parent-child edges
- child dependency edges
- child origin metadata
- materialization summary for the parent

On no-op:

- confirmation that the existing child set already matches the authoritative layout

On structural conflict:

- explicit replan or reconciliation requirement

On invalid layout:

- failure result with dependency or structure diagnostics

---

## Durable writes

- child node-version rows
- parent-child relationship rows
- child dependency edge rows
- child origin metadata such as `layout_generated`
- parent materialization event/summary
- reconciliation-required event where applicable

---

## Happy path

```text
function materialize_layout_children(parent_node_version_id, layout):
  parent = load_parent_node_version(parent_node_version_id)
  authority_mode = classify_parent_child_authority(parent_node_version_id)
  existing_children = load_existing_children(parent_node_version_id)

  validate_layout_shape(layout, parent)
  validate_dependency_graph(parent_node_version_id, layout.children)

  if authority_mode == "hybrid":
    record_reconciliation_required(
      parent_node_version_id,
      reason = "hybrid_tree_requires_explicit_reconciliation"
    )
    return MaterializationResult(status = "reconciliation_required")

  if authority_mode == "manual":
    record_reconciliation_required(
      parent_node_version_id,
      reason = "manual_tree_has_no_layout_authority"
    )
    return MaterializationResult(status = "reconciliation_required")

  if layout_matches_existing_materialization(layout, existing_children):
    record_materialization_noop(parent_node_version_id, layout.hash)
    return MaterializationResult(status = "already_materialized")

  if existing_children and not layout_matches_existing_materialization(layout, existing_children):
    record_replan_required(parent_node_version_id, reason = "layout_changed_after_materialization")
    return MaterializationResult(status = "replan_required")

  begin_transaction()

  created_children = []
  for child_spec in ordered_layout_children(layout):
    child = create_child_node_version(
      parent_node_version_id = parent_node_version_id,
      child_kind = child_spec.kind,
      child_tier = child_spec.tier,
      child_title = child_spec.title,
      child_origin = "layout_generated"
    )
    persist_parent_child_edge(parent_node_version_id, child.id, origin_type = "layout_generated")
    created_children.append(child)

  for child_spec in layout.children:
    for dep in child_spec.dependencies:
      target = resolve_materialized_child_by_layout_id(created_children, dep.target_child_id)
      persist_child_dependency_edge(
        source_child_id = resolve_materialized_child_by_layout_id(created_children, child_spec.id).id,
        target_child_id = target.id,
        dependency_type = dep.type,
        required_state = dep.required_state or "COMPLETE"
      )

  persist_materialization_summary(parent_node_version_id, layout.hash, created_children)
  commit_transaction()

  return MaterializationResult(status = "created", child_count = len(created_children))
```

---

## Validation rules

Before any child is created, validate:

- unique child IDs in the layout
- allowed child kinds and tiers under the parent constraints
- legal dependency references
- no self-dependencies
- no cycles
- no missing targets
- no invalid relative dependency types

The module must fail fast. Partial materialization should not become authoritative.

---

## Authority and reconciliation behavior

- fully layout-driven parent: layout may materialize children directly
- fully manual parent: layout cannot silently replace the child set
- hybrid parent: automatic structural replacement is blocked until explicit reconciliation

This is where the system prevents silent fights between layout regeneration and manual edits.

---

## Failure paths

### Invalid layout

- return failure without creating children
- preserve validation outcome such as `invalid_cycle` or `invalid_target`

### Authority conflict

- return `reconciliation_required`
- do not mutate the child set

### Changed layout after prior materialization

- return `replan_required`
- do not mutate existing children in place

### Persistence failure

- rollback transaction
- do not leave a partial child set authoritative

---

## Pause/recovery behavior

- this module should not pause inside the transaction
- if explicit reconciliation is required, return a control result that the parent loop may convert into pause or replanning
- reruns should be idempotent against the same parent version and layout hash

---

## CLI-visible expectations

Operators should be able to query:

- current child-set authority mode
- current layout hash
- whether materialization already happened
- why materialization was blocked or failed
- which children and dependency edges were created

---

## Open questions

- whether a fully manual parent should always reject layout materialization or permit an explicit “adopt layout now” transition
- whether unchanged existing children can ever be reused automatically after a layout change without full replanning

---

## Pseudotests

### `materializes_children_for_layout_authoritative_parent`

Given:

- parent authority mode is `layout_authoritative`
- layout is valid

Expect:

- child nodes and dependency edges are created
- child origin is `layout_generated`

### `blocks_materialization_for_hybrid_parent`

Given:

- parent authority mode is `hybrid`

Expect:

- no structural mutation occurs
- reconciliation requirement is recorded

### `fails_fast_on_dependency_cycle`

Given:

- layout children contain a cycle

Expect:

- no child nodes are created
- validation outcome records cycle failure
