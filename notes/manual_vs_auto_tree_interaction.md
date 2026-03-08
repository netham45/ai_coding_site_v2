# Manual Vs Auto Tree Interaction

## Purpose

This document defines how manually created node trees should coexist with automatically generated layout-driven trees.

The design already requires both:

- automatic decomposition through layouts
- manual creation of nodes at any level

What remained underspecified was how they interact when they coexist in the same subtree or project.

Related documents:

- `notes/node_lifecycle_spec_v2.md`
- `notes/yaml_schemas_spec_v2.md`
- `notes/child_materialization_and_scheduling.md`
- `notes/invalid_dependency_graph_handling.md`
- `notes/cross_spec_gap_matrix.md`

---

## Core Rule

Manual and automatic tree construction should be compatible, but the source of structural authority must always be explicit.

That means:

- a node’s child set should have a clear source of truth
- the system should not silently overwrite manual children because a layout was regenerated
- the system should not silently ignore layout changes because manual children happen to exist

The tree must remain structurally explainable.

---

## Child-Origin Types

The design should distinguish explicitly:

- `manual`
- `layout_generated`
- `layout_generated_then_modified`

These should now be treated as canonical persisted values or equivalent bounded metadata.

Reason:

- regeneration and replan behavior differs depending on child origin

---

## Source Of Structural Authority

For any given parent node version, the child set should have one of the following authority models.

## Model 1: Fully manual

Meaning:

- children were created manually
- no layout is currently authoritative for the child set

## Model 2: Fully layout-driven

Meaning:

- the active child set was materialized from a layout
- layout is authoritative for structural changes

## Model 3: Hybrid with explicit manual override

Meaning:

- the child set originated from a layout
- one or more structural edits were then made manually
- the system must treat the tree as hybrid until an explicit reconciliation occurs

Recommended default:

- allow hybrid, but make it explicit and auditable

---

## Safe Rule For Hybrid Trees

If a layout-generated child set has been manually altered, the system should not silently treat the old layout as still fully authoritative.

Instead:

- mark the tree as hybrid
- require explicit reconciliation before future layout-driven regeneration changes the same child set

This avoids invisible fights between:

- layout regeneration
- manual edits

---

## Manual Creation Behavior

When a user manually creates a child under a parent:

1. validate that parent-child constraints allow it
2. persist the child and parent-child edge
3. classify the child origin as manual
4. if the parent previously had a layout-authoritative child set, mark the parent as hybrid unless policy explicitly forbids mixed mode

The system should not pretend the layout automatically “contained” the new child unless the layout is explicitly updated.

---

## Layout Regeneration Behavior In Mixed Trees

If a parent with hybrid child origin regenerates or regenerates its layout:

Recommended default:

1. detect hybrid status
2. pause automatic structural replacement
3. require explicit reconciliation decision

Possible reconciliation choices:

- adopt the new layout as authoritative and supersede conflicting manual children
- preserve manual children and require layout update
- merge the new layout and manual changes into a new explicit authoritative structure

The system should not silently choose one.

---

## Layout Reconciliation Triggers

Reconciliation should be triggered when:

- a parent layout changes after manual edits
- a user manually creates/removes/reorders children in a layout-driven subtree
- dependency edges conflict with the latest layout
- child set no longer matches the authoritative layout hash

At that point, the parent should either:

- enter a replan/review flow
- or pause for user if the conflict is structural and ambiguous

---

## Dependency Handling Rule

Dependency rules should not care whether a child is manual or layout-generated.

They should care only that:

- the child graph is valid
- dependency edges are legal
- authority resolution is clear

Origin affects structural reconciliation, not dependency legality.

---

## Scheduling Rule

Scheduling should also be origin-agnostic.

If a child exists and is valid:

- it can be scheduled based on readiness

Origin matters for:

- regeneration
- child-set reconciliation
- layout authority

Origin should not matter for:

- whether the child is runnable

---

## Regeneration Rule

When a parent is regenerated:

### Fully manual parent

- preserve manual child structure unless user or policy explicitly changes it

### Fully layout-driven parent

- regenerate child structure from authoritative layout

### Hybrid parent

- require explicit reconciliation before structural child regeneration changes are applied

Recommended default:

- hybrid trees should not auto-regenerate structure without an explicit decision

---

## Child Removal Or Replacement

If a layout no longer includes a child that exists manually or in hybrid form:

The system should not silently delete or orphan it.

Recommended behavior:

- mark the discrepancy
- require explicit reconciliation
- allow operator/user to decide whether the child is:
  - superseded
  - preserved
  - reattached through updated layout

---

## Pseudocode

```python
def classify_parent_child_authority(parent_node_id):
    children = load_children(parent_node_id)
    if all(child.origin == "manual" for child in children):
        return "manual"
    if all(child.origin == "layout_generated" for child in children):
        return "layout_authoritative"
    return "hybrid"


def handle_layout_update(parent_node_id, new_layout):
    authority = classify_parent_child_authority(parent_node_id)
    if authority == "manual":
        return pause_for_user(parent_node_id, reason="manual_tree_has_no_layout_authority")

    if authority == "hybrid":
        return pause_for_user(parent_node_id, reason="hybrid_tree_requires_reconciliation")

    return materialize_layout_children(parent_node_id, new_layout)
```

---

## DB Implications

The current DB model does not yet explicitly track child origin or child-set authority.

Possible additions if this remains important:

### Option 1: origin metadata on child relationship

Possible field on `node_children`:

- `origin_type`

### Option 2: parent-level authority metadata

Possible conceptual values:

- `manual`
- `layout_authoritative`
- `hybrid`

This could live:

- on parent node metadata
- in a separate child-set metadata structure

Recommended current direction:

- explicit origin/authority metadata is required if hybrid trees are supported

---

## CLI Implications

Operators should be able to inspect:

- whether a parent’s child set is manual, layout-driven, or hybrid
- whether current children match the authoritative layout
- whether reconciliation is required

Likely useful capabilities:

- `ai-tool node children --node <id> --verbose`
- `ai-tool layout show --node <id>`
- maybe `ai-tool node structure-status --node <id>`

If names differ, the capability should still exist.

---

## Recommended Default Product Stance

To reduce complexity, the simplest safe first-implementation stance is:

1. support fully manual trees
2. support fully layout-driven trees
3. allow hybrid trees only as an explicitly paused/reconciliation-required state

This avoids needing fully automatic merge behavior between manual edits and layout regeneration in the first implementation.

---

## Open Decisions Still Remaining

### D01. Whether hybrid child origin needs explicit DB support in v1

Recommended direction:

- yes if hybrid is allowed at all

### D02. Whether manual child insertion should be allowed into layout-authoritative parents without immediate pause

Recommended direction:

- likely yes, but it should immediately mark the parent as hybrid

### D03. Whether automatic reconciliation should ever happen

Recommended direction:

- no in first implementation

---

## Recommended Next Follow-On Work

The next docs that should absorb this logic are:

1. `notes/node_lifecycle_spec_v2.md`
2. `notes/child_materialization_and_scheduling.md`
3. `notes/database_schema_spec_v2.md`
4. `notes/cross_spec_gap_matrix.md`

Then reduce the severity of the manual-vs-auto tree interaction gap.

---

## Exit Criteria

This note is complete enough when:

- structural authority is explicit
- hybrid behavior is explicit
- regeneration behavior for each model is explicit
- DB and CLI implications are identified

At that point, manual and automatic tree construction can coexist without hidden structural ambiguity.
