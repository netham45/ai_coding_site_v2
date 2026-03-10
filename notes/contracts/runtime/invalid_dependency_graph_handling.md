# Invalid Dependency Graph Handling

## Purpose

This document defines how the system should detect and respond to invalid dependency graphs.

The design already allows:

- child dependencies
- sibling dependencies

And it disallows:

- parent dependencies
- cousin dependencies
- arbitrary distant dependency edges

But the exact validation and failure behavior for invalid graphs remained underspecified. This note makes dependency validation explicit enough to support:

- layout validation
- manual tree validation
- scheduling safety
- compile-time and runtime checks

Related documents:

- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`

---

## Core Rule

Invalid dependency graphs must fail fast and visibly.

Reason:

- dependency bugs can cause deadlocks
- dependency bugs can cause hidden invalid execution order
- dependency bugs are often hard to diagnose if the system tries to “best effort” around them

The system should prefer explicit rejection over silent fallback.

---

## Valid Dependency Rules

The default valid dependency rules are:

- a node may depend on one of its siblings
- a node may depend on one of its children if the model explicitly allows that for the given phase
- a node may not depend on its parent
- a node may not depend on cousins, niblings, or unrelated nodes
- a node may not depend on itself

The exact child-dependency allowance should be explicit in the higher-level model. If child dependencies are allowed, they still must be used carefully and visibly.

---

## What Makes A Dependency Graph Invalid

The system should treat at least the following as invalid.

## D01. Self-dependency

Example:

- node A depends on node A

## D02. Parent dependency

Example:

- child node depends on its parent

## D03. Invalid relative dependency

Example:

- node depends on cousin, nibling, or unrelated subtree node

## D04. Missing target dependency

Example:

- dependency references a child ID not in the materialized set

## D05. Cycle

Example:

- A depends on B
- B depends on C
- C depends on A

## D06. Duplicate edge

Example:

- repeated identical dependency edge for the same pair

## D07. Impossible dependency state requirement

Example:

- dependency requires a state not supported by the model

## D08. Cross-version ambiguity

Example:

- dependency target does not clearly refer to the authoritative version of a node

---

## Where Dependency Validation Should Happen

Dependency validation should happen in multiple places.

## Stage 1: Layout validation

When a layout is created or reviewed, validate dependency references before child materialization.

## Stage 2: Child materialization

When dependency edges are persisted, validate that the target children exist and the edges are allowed.

## Stage 3: Run admission

When a node is being admitted to run, validate that its dependencies are still structurally valid and resolvable.

## Stage 4: Scheduling/runtime sanity checks

If runtime detects contradictory blocker state or impossible dependency resolution, it should surface it rather than waiting forever.

---

## Compile-Time vs Runtime Rule

The system should catch dependency problems as early as possible.

### Compile/layout-time

Catch:

- unknown dependency IDs
- duplicate edges
- obvious disallowed relative types
- obvious cycles within a declared child layout

### Runtime-time

Catch:

- stale or superseded dependency targets
- authoritative-version ambiguity
- unexpected impossible wait conditions

The runtime should not assume compile-time validation made all future dependency problems impossible.

---

## Cycle Detection Rule

Dependency cycles should be treated as hard errors.

Recommended default:

- detect cycles during layout validation or child materialization
- if a cycle is detected, fail the layout/materialization step

The system should not try to “break” cycles automatically.

Reason:

- automatic cycle breaking hides planning errors

---

## Missing Dependency Targets

If a dependency points to a target that does not exist:

- materialization should fail if discovered before persistence
- otherwise validation should fail before scheduling

The system should not silently ignore the dependency.

---

## Authoritative-Version Rule

Dependencies should resolve against the authoritative current version of the target node, not merely the latest created candidate.

This matters especially during:

- rectification
- supersession
- mixed old/new lineage states

If the runtime cannot determine the authoritative dependency target unambiguously:

- it should pause or fail validation
- it should not guess

---

## Runtime Impossible-Wait Detection

The runtime should detect when a node is waiting on something that can never resolve under the current graph.

Examples:

- dependency target is failed and no recovery path exists
- dependency target is superseded and no authoritative replacement is selected
- dependency target is structurally invalid

In these cases, the system should:

- not wait indefinitely
- surface a dependency failure
- route through parent failure or user-facing pause logic as appropriate

---

## Validation Outcomes

Dependency validation should classify outcomes as:

- `valid`
- `invalid_structure`
- `invalid_target`
- `invalid_cycle`
- `invalid_authority`
- `runtime_impossible_wait`

These can map to implementation-specific values, but the distinction should exist conceptually.

---

## Pseudocode

```python
def validate_dependency_graph(parent_node_id, child_specs):
    ensure_unique_child_ids(child_specs)
    ensure_all_dependency_targets_exist(child_specs)
    ensure_no_self_dependencies(child_specs)
    ensure_allowed_relative_dependency_types(parent_node_id, child_specs)
    ensure_no_cycles(child_specs)
    return "valid"


def validate_runtime_dependency_target(node_id):
    dependencies = load_dependencies(node_id)
    for dep in dependencies:
        target = resolve_authoritative_target(dep)
        if target is None:
            return "invalid_authority"
        if is_impossible_wait(target):
            return "runtime_impossible_wait"
    return "valid"
```

---

## Parent And Child Failure Interaction

If a dependency graph is invalid:

- this is not a transient child execution failure
- it likely indicates:
  - bad layout
  - bad manual tree construction
  - bad replan output

Recommended handling:

- treat as structural/planning failure
- route toward parent replan or pause for user rather than blind child retry

This should integrate with the parent failure classification model.

---

## DB Implications

The current DB model now supports dependency storage and the latest persisted blocker surface with:

- `node_dependencies`
- `node_dependency_blockers`

The current implementation uses `node_dependency_blockers` as a replace-on-write current snapshot for the authoritative node version being checked.

Useful views:

- blocked nodes by dependency target
- invalid dependency resolution candidates

Potential future artifact:

- historical dependency validation result rows if blocker history becomes operationally important beyond the latest snapshot

---

## CLI Implications

Useful CLI capabilities:

- `ai-tool node dependencies --node <id>`
- `ai-tool node dependency-status --node <id>`
- `ai-tool node dependency-validate --node <id>`
- `ai-tool node blockers --node <id>`

These should be enough to answer:

- what dependencies exist
- whether they are valid
- why a node is blocked

---

## Manual Tree Interaction

Manual tree construction should be subject to the same dependency validation rules as layout-generated children.

The scheduler should not assume manual trees are safer or more trusted.

Every dependency edge should still be validated for:

- relationship legality
- cycle freedom
- target existence
- authority resolution

---

## Open Decisions Still Remaining

### D01. Child dependencies versus sibling-only dependencies

Recommended current direction:

- keep sibling dependencies as the common path
- allow child dependencies only if there is a clear runtime need and the semantics remain simple

### D02. Dedicated dependency validation result table

Recommended current direction:

- not required initially
- use validation results plus CLI first

### D03. Automatic graph repair

Recommended current direction:

- do not auto-repair invalid graphs

---

## Recommended Next Follow-On Work

The next docs that should absorb this logic are:

1. `notes/specs/runtime/node_lifecycle_spec_v2.md`
2. `notes/specs/database/database_schema_spec_v2.md`
3. `notes/specs/cli/cli_surface_spec_v2.md`
4. `notes/catalogs/traceability/cross_spec_gap_matrix.md`

Then reduce the severity of the invalid-dependency-graph gap.

---

## Exit Criteria

This note is complete enough when:

- invalid graph classes are explicit
- validation stages are explicit
- runtime impossible-wait handling is explicit
- authoritative-target resolution is explicit

At that point, dependency safety is no longer an implicit assumption.
