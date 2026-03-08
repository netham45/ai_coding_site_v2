# Module: `schedule_ready_children(...)`

## Purpose

Classify already-materialized children by readiness and start the eligible set according to dependency and policy constraints.

This module owns readiness and scheduling. It does not create child structure.

---

## Source notes

Primary:

- `notes/child_materialization_and_scheduling.md`
- `notes/invalid_dependency_graph_handling.md`

Supporting:

- `notes/node_lifecycle_spec_v2.md`
- `notes/runtime_command_loop_spec_v2.md`
- `notes/state_value_catalog.md`

---

## Inputs

- `parent_node_version_id`
- active child set
- authoritative dependency edges
- current child lifecycle states
- parent scheduling policy such as `auto_run_children` and concurrency limits

---

## Required state

- child set is already materialized
- dependency graph is structurally valid or a runtime-visible invalidity has already been recorded
- authoritative child versions are resolvable

---

## Outputs

- per-child scheduling classification
- optional set of children started this cycle
- parent-visible blocker summary

---

## Durable writes

- scheduling classification records or equivalent derived read-model updates
- child start/admission events for the ready set
- impossible-wait or dependency-block events where applicable

---

## Happy path

```text
function schedule_ready_children(parent_node_version_id):
  children = load_authoritative_children(parent_node_version_id)
  policy = load_child_scheduling_policy(parent_node_version_id)

  classifications = []
  ready_children = []

  for child in children:
    classification = classify_child_scheduling_state(child, children)
    classifications.append(classification)

    if classification.status == "ready":
      ready_children.append(child)

  persist_child_scheduling_snapshot(parent_node_version_id, classifications)

  if policy.auto_run_children is false:
    return SchedulingResult(status = "classified_only", ready_children = ready_children)

  admitted = []
  for child in ready_children:
    if concurrency_limit_reached(parent_node_version_id, admitted, policy):
      break
    admit_child_run(child.id)
    admitted.append(child.id)

  return SchedulingResult(
    status = "scheduled",
    ready_children = [child.id for child in ready_children],
    started_children = admitted
  )
```

---

## Classification rules

Each child should classify as one of:

- `ready`
- `blocked_on_dependency`
- `already_running`
- `complete`
- `failed`
- `superseded`
- `paused_for_user`
- `not_compiled`

The classification should be driven by:

- authoritative child status
- whether the child is already running
- whether all required dependencies are `COMPLETE`
- whether a blocking impossible-wait condition exists

---

## Dependency readiness rule

Default rule:

- each required dependency target must be in `COMPLETE`

Do not require sibling completion that is not represented by explicit dependency edges.

---

## Impossible-wait behavior

If a child is blocked on a dependency that can never satisfy the required state under current authoritative lineage:

- do not classify it as ordinary `blocked_on_dependency`
- classify the condition as `runtime_impossible_wait`
- surface it to the parent failure or pause path

Examples:

- target child failed with no remaining recovery path
- target child is superseded and authoritative replacement is unresolved
- target child reference is structurally invalid at runtime

---

## Failure paths

### Runtime authority ambiguity

- if dependency target authority is ambiguous, do not guess
- record invalid authority or impossible-wait condition

### Invalid child state combination

- if a child appears both active and complete, treat as invariant failure
- stop automated scheduling for that child until corrected

### Admission failure for a ready child

- preserve the ready classification
- record admission failure separately

---

## Pause/recovery behavior

- this module should be repeatable as dependencies resolve
- rerunning it should not duplicate child starts if a child is already running
- scheduling snapshots should remain explainable across recovery or restart

---

## CLI-visible expectations

Operators should be able to ask:

- which children are ready now
- which are blocked and by whom
- which are impossible to satisfy under current lineage
- which were started automatically versus only classified

---

## Open questions

- whether scheduling classifications need dedicated persistence or can be derived cheaply enough from authoritative state plus dependency edges
- how aggressively runtime should auto-reschedule after child completion events versus operator- or parent-triggered passes

---

## Pseudotests

### `classifies_ready_children_without_requiring_unrelated_sibling_completion`

Given:

- child A has no unsatisfied dependencies
- sibling B is incomplete but not a dependency

Expect:

- child A is `ready`

### `does_not_restart_already_running_child`

Given:

- child is already running

Expect:

- classification is `already_running`
- no new start occurs

### `surfaces_runtime_impossible_wait_instead_of_waiting_forever`

Given:

- a dependency target is failed with no viable recovery path

Expect:

- child is not treated as ordinary blocked
- impossible-wait condition is surfaced
