# Module: `check_node_dependency_readiness(...)`

## Purpose

Determine whether a node is structurally and operationally ready to start execution based on its authoritative dependency set.

This module answers readiness only. It does not create a run.

---

## Source notes

Primary:

- `notes/node_lifecycle_spec_v2.md`
- `notes/invalid_dependency_graph_handling.md`

Supporting:

- `notes/child_materialization_and_scheduling.md`
- `notes/cutover_policy_note.md`
- `notes/state_value_catalog.md`

---

## Inputs

- `node_version_id`
- authoritative dependency edges for the node
- authoritative version selectors for dependency targets
- current target lifecycle states

---

## Required state

- dependency edges are queryable
- authoritative target version can be resolved for each dependency
- dependency required state vocabulary is bounded and known

---

## Outputs

- `DependencyReadinessResult(status = "ready" | "blocked" | "invalid" | "impossible_wait")`

Optional outputs:

- blocking dependency IDs
- blocker reasons
- invalid-authority diagnostics

---

## Durable writes

- dependency-readiness snapshot or blocker summary where useful
- impossible-wait or invalid-authority event where applicable

---

## Decision algorithm

```text
function check_node_dependency_readiness(node_version_id):
  dependencies = load_authoritative_dependencies(node_version_id)

  if dependencies is empty:
    return DependencyReadinessResult(status = "ready")

  blockers = []

  for dep in dependencies:
    target = resolve_authoritative_dependency_target(dep)
    if target is null:
      record_invalid_dependency_authority(node_version_id, dep)
      return DependencyReadinessResult(status = "invalid", dependency_id = dep.id)

    if dependency_target_can_never_satisfy_required_state(target, dep.required_state):
      record_impossible_wait(node_version_id, dep, target.id)
      return DependencyReadinessResult(status = "impossible_wait", dependency_id = dep.id)

    if not dependency_target_satisfies_required_state(target, dep.required_state):
      blockers.append({
        dependency_id: dep.id,
        target_id: target.id,
        required_state: dep.required_state
      })

  if blockers:
    persist_dependency_blockers(node_version_id, blockers)
    return DependencyReadinessResult(status = "blocked", blockers = blockers)

  persist_dependency_ready_snapshot(node_version_id)
  return DependencyReadinessResult(status = "ready")
```

---

## Default required-state rule

First-pass default:

- a dependency is satisfied only when its authoritative target is `COMPLETE`

Do not infer readiness from softer states unless policy explicitly expands the vocabulary.

---

## Failure paths

### Invalid authority

- authoritative target cannot be resolved cleanly
- do not guess which version should satisfy the dependency

### Impossible wait

- target failed without viable recovery
- target is superseded without authoritative replacement
- target state can never satisfy required state under current model

### Ordinary blocker

- target exists and is valid
- target simply is not complete yet

---

## Pause/recovery behavior

- readiness should be recomputable from durable state after restart
- invalid or impossible dependency conditions should not degrade into ordinary waiting after recovery

---

## CLI-visible expectations

Operators should be able to inspect:

- which dependencies are blocking run admission
- whether the blocker is ordinary, invalid, or impossible
- which authoritative target version is being considered

---

## Pseudotests

### `returns_ready_when_all_dependencies_are_complete`

Given:

- all authoritative dependency targets are `COMPLETE`

Expect:

- readiness result is `ready`

### `returns_blocked_for_ordinary_incomplete_dependency`

Given:

- target exists and is authoritative
- target is incomplete but still resolvable

Expect:

- readiness result is `blocked`

### `returns_impossible_wait_when_target_cannot_recover`

Given:

- dependency target has failed with no viable recovery path

Expect:

- readiness result is `impossible_wait`
