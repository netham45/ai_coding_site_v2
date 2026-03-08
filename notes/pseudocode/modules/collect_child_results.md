# Module: `collect_child_results(...)`

## Purpose

Gather the authoritative outputs, summaries, final commits, and result statuses of a parent's children so the parent can decide whether it is ready to reconcile, must wait, or must react to failure.

This module is read-heavy and decision-oriented. It does not itself merge children into the parent branch.

---

## Source notes

Primary:

- `notes/child_materialization_and_scheduling.md`
- `notes/runtime_command_loop_spec_v2.md`
- `notes/git_rectification_spec_v2.md`

Supporting:

- `notes/parent_failure_decision_spec.md`
- `notes/cutover_policy_note.md`
- `notes/state_value_catalog.md`

---

## Inputs

- `parent_node_version_id`
- authoritative child set for the parent
- child final commit metadata
- child summary and result records
- parent policy for required children and reusable healthy children

---

## Required state

- the parent's authoritative child set is known
- the authoritative version of each child is resolvable
- child run status, lifecycle state, summaries, and final commits are queryable

---

## Outputs

- child result snapshot keyed by child ID
- per-child reconciliation readiness classification
- parent-level summary of:
  - complete children
  - failed children
  - paused children
  - waiting children
  - reusable final commits

---

## Durable writes

- child result snapshot or equivalent derived summary record
- parent-visible reconciliation-input summary

---

## Happy path

```text
function collect_child_results(parent_node_version_id):
  children = load_authoritative_children(parent_node_version_id)
  snapshot = []

  for child in children:
    authoritative_child = resolve_authoritative_child_version(child.logical_node_id)
    result = {
      child_id: authoritative_child.id,
      lifecycle_state: load_node_lifecycle_state(authoritative_child.id),
      run_status: load_latest_run_status(authoritative_child.id),
      final_commit_sha: load_current_final_commit(authoritative_child.id),
      latest_summary: load_latest_child_summary(authoritative_child.id),
      dependency_impact: load_child_dependency_impact(authoritative_child.id)
    }
    result.reconcile_status = classify_child_result_for_parent(result)
    snapshot.append(result)

  persist_child_result_snapshot(parent_node_version_id, snapshot)
  return ChildResultCollection(status = "ok", snapshot = snapshot)
```

---

## Classification rules

Each child should classify for parent reconciliation as one of:

- `ready_for_reconcile`
- `waiting`
- `failed`
- `paused`
- `superseded_with_authoritative_replacement`
- `invalid_authority`

The parent should not treat a child as ready if:

- its authoritative version is ambiguous
- its final commit is unavailable when one is required
- its status is failed or paused

---

## Failure paths

### Ambiguous authoritative child version

- do not guess which child version to consume
- classify as `invalid_authority`
- force parent pause or validation failure upstream

### Missing final commit on apparently complete child

- treat as invariant violation
- do not feed the child into merge planning

### Stale child result view

- recompute from authoritative child state
- avoid relying on stale cached summaries when authority changed

---

## Pause/recovery behavior

- rerunning collection after recovery should reproduce the same snapshot from durable child state
- candidate child versions should not replace authoritative child results until cutover occurs

---

## CLI-visible expectations

Operators should be able to inspect:

- which child results the parent currently considers authoritative
- which children are ready to merge
- which children are blocked, failed, or ambiguous

---

## Open questions

- whether child result snapshots should be fully persisted or derived on demand
- whether parent reconciliation should consume only authoritative children or allow candidate-lineage previews in special review modes

---

## Pseudotests

### `collects_only_authoritative_child_results`

Given:

- a child has both candidate and authoritative versions

Expect:

- the authoritative version is selected for parent reconciliation inputs

### `surfaces_invalid_authority_instead_of_guessing`

Given:

- the authoritative child version is ambiguous

Expect:

- collection marks invalid authority
- parent reconciliation is blocked
