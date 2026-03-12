# Child Materialization And Scheduling

## Purpose

This document defines how parent nodes should turn layouts into child nodes and how the runtime should decide when those children are eligible to start.

This is one of the most important remaining open orchestration gaps because the broader system depends on:

- layout-driven decomposition
- valid dependency graphs
- concurrent child execution where possible
- deterministic parent waiting and reconciliation behavior

Related documents:

- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`

---

## Core Rule

Child materialization and child scheduling are separate concerns.

### Materialization

Means:

- converting a layout into durable child node versions and dependency edges

### Scheduling

Means:

- deciding which already-materialized children are eligible to start now

This distinction matters because:

- materialization may happen once
- scheduling may happen repeatedly as dependencies resolve

---

## Child Materialization Inputs

The parent should materialize children using:

- parent node version ID
- compiled workflow or current task context
- resolved layout definition
- parent/child constraint rules
- project policy affecting child auto-run behavior

The materialization step must not rely on ad hoc in-session memory.

---

## Layout Preconditions

Before materializing children, the runtime should validate the layout.

The layout should be checked for:

- unique child IDs within the layout
- valid child kinds and tiers under parent constraints
- valid dependency references
- no self-dependencies
- no dependency cycles within the child set
- valid ordinals where ordering is used

If the layout is invalid:

- child materialization must fail
- the failure should be visible to the parent
- no partial child tree should be treated as authoritative

---

## Materialization Output

Successful child materialization should produce:

- child node versions
- parent-child edges
- child dependency edges
- any required initial branch or seed metadata
- initial child statuses

Recommended default initial child lifecycle state:

- `COMPILED` if child workflow compiles immediately on creation
- otherwise `DRAFT` until compilation occurs

Recommended parent-side output:

- a summary or durable record showing which children were created and which dependencies exist

---

## Idempotency Rule

Child materialization should be idempotent relative to a given parent version and layout version.

That means:

- rerunning the materialization step should not create duplicate children if nothing changed
- a rerun should either:
  - detect that the current materialized set already matches the layout
  - or explicitly reconcile differences if the layout changed

This is important for:

- retry safety
- recovery
- parent replan flows

Implementation staging note:

- the current implementation keys idempotency off the authoritative parent node version plus the SHA-256 of the effective resolved layout document
- effective layout resolution now prefers `layouts/generated_layout.yaml` under the configured workspace root when that file exists
- the packaged built-in layout for the parent kind remains the fallback when no generated layout file exists
- `node_children.layout_child_id` stores the exact layout child id so reruns do not have to infer identity from mutable child titles
- if child rows already exist while the authoritative layout hash is missing, the parent is treated as `reconciliation_required` rather than silently rematerialized

---

## Layout Change Behavior

If the layout changes after children were already materialized, the runtime should not silently mutate the existing child set in place.

Recommended behavior:

1. detect that the layout differs from the materialized child set
2. treat this as a parent replan or regeneration event
3. explicitly decide which children are:
   - unchanged and reusable
   - superseded
   - newly required
   - removed or no longer relevant

This avoids hidden structural drift between layout and child tree.

---

## Scheduling Eligibility Rule

A child is eligible to start when all of the following are true:

- the child exists and is not superseded
- the child is compiled and runnable
- the child is not already complete
- the child is not already actively running
- all required dependencies are satisfied
- no blocking parent policy prevents start

The runtime should not require sibling completion unless dependency rules actually require it.

---

## Dependency Readiness

By default, dependency readiness should mean:

- each required dependency child is in `COMPLETE`

This should be simple unless a later use case truly requires more granular dependency states.

Implementation extension note:

- sibling dependencies between materialized children that share a parent lineage now require merge-backed satisfaction rather than raw sibling lifecycle alone
- for those sibling edges, a prerequisite child reaching `COMPLETE` is not enough; the prerequisite child must also have a durable successful incremental merge row into the authoritative parent lineage the dependent child will start from
- operator-visible blocker kinds for that path now include:
  - `blocked_on_incremental_merge`
  - `blocked_on_merge_conflict`
  - `blocked_on_parent_refresh`
- non-sibling dependency edges and sibling edges without a shared parent lineage remain on the existing lifecycle-based `required_state` rule in the current implementation slice
- if a dependent child was already bootstrapped from an older parent head before the prerequisite sibling merged upward, admission must block that child on `blocked_on_parent_refresh` until the child bootstrap is refreshed against the current parent merge-lane head
- if a sibling dependency invalidates a dependent node deeply enough that its own decomposition assumptions are stale, the dependent node must restart from a fresh node version with no reused child tree and remain blocked in the sibling-dependency wait state until parent refresh plus fresh child rematerialization complete
- current implementation note: once that fresh dependency-invalidated version becomes authoritative, the background incremental-merge/refresh loop now refreshes it from the updated parent head and, for layout-authoritative prior child trees, rematerializes its children from an empty tree before transitioning it out of the sibling wait state
- current implementation note: if a placeholder `manual` authority row was carried onto that fresh version during rebuild remap, the authoritative follow-on path must reset it back to `layout_authoritative` before rematerialization so stale child lineage is not silently reused
- current implementation note: if the superseded version's child authority was `manual` or `hybrid`, the fresh dependency-invalidated version must remain blocked with `child_tree_rebuild_required` after parent refresh; the daemon must not auto-transition it to `READY` because no safe automatic child-tree rebuild path exists yet for those modes
- current implementation note: that manual/hybrid rebuild gate is now cleared only by explicit fresh-version structural work, not by refresh alone; either new manual child creation on the fresh authoritative version or `node reconcile-children --node <id> --decision preserve_manual` on the empty fresh version can satisfy the rebuild requirement

---

## Scheduling Outcomes

For each child, scheduling should classify it as one of:

- `ready`
- `blocked_on_dependency`
- `already_running`
- `complete`
- `failed`
- `superseded`
- `paused_for_user`
- `not_compiled`

These classifications should be visible to the parent for orchestration and debugging.

Implementation note:

- the current implementation now exposes richer per-child scheduling explanation through `node child-materialization --node <id>`
- each child row includes:
  - `scheduling_status`
  - `scheduling_reason`
  - the current blocker list
- current tree/operator reads also expose summarized scheduling visibility through:
  - `tree show --node <id> --full`
  - `node blockers --node <id>`

---

## Parent Runtime Behavior

After materialization, the parent should:

1. identify all ready children
2. start ready children if `auto_run_children` is enabled
3. otherwise expose them as ready for explicit operator/user start
4. wait for blocked children to become ready
5. react to child completion or failure
6. proceed to reconciliation only when required children are complete

The parent should not busy-loop blindly. The scheduling mechanism may be:

- event-driven
- polling-based
- hybrid

But the durable model should look the same either way.

Implementation staging note:

- the current daemon now runs a background child auto-start loop
- parent-generated child layouts are no longer treated as authoritative merely because `layouts/generated_layout.yaml` exists in the workspace
- the current runtime requires an explicit parent-side registration step before the generated layout becomes authoritative for materialization
- after child materialization, the daemon scans authoritative parent-child edges, evaluates readiness from durable child state, and auto-starts only children that are actually `ready`
- before that auto-start bind step, the daemon now runs a pre-pass that advances pending parent incremental merges and auto-refreshes blocked `blocked_on_parent_refresh` children when they are inactive and covered by auto-run policy
- the current implementation admits the child run with trigger reason `auto_run_child` and binds a primary session immediately
- dependency-blocked siblings remain unstarted until their dependencies clear
- if a blocked sibling depends on another child that will change the parent branch or parent context, the parent must merge that prerequisite child back into parent state before admitting the dependent sibling
- this incremental merge step is separate from the later full `wait_for_children` plus `reconcile_children` stage; it exists so dependent siblings do not start from stale parent ancestry or stale parent-visible artifacts

---

## Required-Children Completion Rule

The parent may continue only when the children required for the current parent task are complete.

That means:

- not every child must necessarily be complete if parent policy/layout scope says otherwise
- but the default semantic ladder likely assumes all current layout children are required

Recommended default:

- all materialized children for the active layout must complete before parent reconciliation

Implementation staging note:

- the current scheduling read path derives child readiness from `node_dependencies`, `node_dependency_blockers`, and each child lifecycle row
- no standalone scheduling snapshot table is currently required because the derived state has been sufficient for operator and parent inspection
- the final parent-local reconcile stage still waits for all required children, but that does not remove the need for earlier incremental merge-to-parent work when sibling dependencies require later children to see newly produced parent state

---

## Child Failure During Scheduling

If a child fails:

- the child should no longer be treated as ready
- the parent should classify it as `failed`
- the parent should invoke parent failure decision logic

The scheduling system itself should not silently retry children without going through parent policy.

---

## Concurrency Rule

Any child whose dependencies are satisfied should be eligible to run concurrently with other ready children.

The scheduler should not serialize siblings by default unless:

- dependencies require it
- environment/resource policy requires it
- operator policy limits concurrency

Recommended default:

- maximize concurrency within dependency and policy constraints

---

## Child Materialization Pseudocode

```python
def materialize_layout_children(parent_node_id, layout):
    validate_layout(layout, parent_node_id)

    existing = load_existing_children(parent_node_id)
    if layout_matches_existing(layout, existing):
        return existing

    if existing and not layout_matches_existing(layout, existing):
        enter_parent_replan_flow(parent_node_id)
        return "replan_required"

    created_children = []
    for child_spec in layout.children:
        child = create_child_node(parent_node_id, child_spec)
        created_children.append(child)

    for child_spec in layout.children:
        persist_child_dependencies(parent_node_id, child_spec)

    register_materialization_summary(parent_node_id, created_children, layout)
    return created_children
```

---

## Child Scheduling Pseudocode

```python
def schedule_ready_children(parent_node_id):
    children = load_children(parent_node_id)
    decisions = []

    for child in children:
        state = classify_child_schedulability(child)
        decisions.append((child.id, state))

        if state == "ready" and parent_auto_run_enabled(parent_node_id):
            start_child_run(child.id)

    persist_parent_child_schedule_snapshot(parent_node_id, decisions)
    return decisions
```

---

## DB Implications

The current DB already supports much of this through:

- `node_versions`
- `node_children`
- `node_dependencies`

Possible useful additions if needed:

### `layout_materializations`

Purpose:

- record that a specific layout was turned into a specific child set

Possible fields:

- `id`
- `parent_node_version_id`
- `layout_hash`
- `summary`
- `created_at`

### `child_schedule_snapshots`

Purpose:

- capture parent-visible scheduling state over time

This may be optional if the combination of child state plus dependency state is sufficient.

Current canonical direction:

- child origin and parent child-authority should be persisted explicitly
- scheduling snapshots may remain optional if derived current-state surfaces are sufficient

Recommended first stance:

- do not add new tables unless the current model proves too opaque

---

## CLI Implications

Useful CLI capabilities:

- `ai-tool layout show --node <id>`
- `ai-tool node children --node <id>`
- `ai-tool node blockers --node <id>`
- `ai-tool node dependency-status --node <id>`

Likely useful additions:

- `ai-tool layout materialize --node <id>`
- `ai-tool node ready-children --node <id>`
- `ai-tool node child-schedule --node <id>`

If names differ, these capabilities should still exist.

---

## Interaction With Manual Trees

If children are created manually rather than from a layout:

- the system should still support scheduling and dependency evaluation
- the materialization step is simply replaced by manual creation
- if a layout-driven parent becomes hybrid, `node child-reconciliation --node <id>` should expose the currently available explicit reconciliation decisions
- the currently supported explicit reconciliation action is `preserve_manual`, which converts the parent to `authority_mode = manual` without silently rewriting the current child set to a new layout

The scheduler should not care whether children came from:

- auto-generated layout
- manual creation

It should care only that:

- the durable child graph exists
- dependency rules are valid

---

## Interaction With Rectification

When a parent or layout changes and children are re-materialized:

- unchanged children may be reusable if policy allows
- affected children may need superseding versions
- scheduling must reference the currently authoritative child lineage

This means materialization and scheduling must stay aware of:

- superseded children
- authoritative children
- candidate rebuilt children
- authoritative versus candidate lineage selectors
- active child inspection surfaces must read the authoritative parent version's `NodeChild` edges, not only the logical `HierarchyNode.parent_node_id` relationship

---

## Open Decisions Still Remaining

### D01. Whether materialization history needs its own table

Recommended current direction:

- materialization history may remain optional
- child origin and parent child-authority metadata should be canonical

### D02. Whether all children are required by default

Recommended current direction:

- yes for the semantic default ladder

### D03. Whether scheduling should be event-driven or polling-driven

Recommended current direction:

- implementation choice, as long as durable behavior is the same

---

## Recommended Next Follow-On Work

The next docs that should absorb this logic are:

1. `notes/specs/runtime/runtime_command_loop_spec_v2.md`
2. `notes/specs/runtime/node_lifecycle_spec_v2.md`
3. `notes/specs/database/database_schema_spec_v2.md`
4. `notes/catalogs/traceability/cross_spec_gap_matrix.md`

Then reduce the severity of the child scheduling gap.

---

## Exit Criteria

This note is complete enough when:

- materialization and scheduling are clearly separated
- layout preconditions are explicit
- readiness classification is explicit
- idempotency and replan behavior are explicit
- DB and CLI implications are identified

At that point, multi-node orchestration is much less ambiguous.
