# Module: `finalize_lineage_cutover(...)`

## Purpose

Transfer authority from an old authoritative lineage to a stable candidate lineage only after the required rebuilt scope is complete, valid, and approved where necessary.

---

## Source notes

Primary:

- `notes/cutover_policy_note.md`
- `notes/git_rectification_spec_v2.md`

Supporting:

- `notes/node_lifecycle_spec_v2.md`
- `notes/runtime_command_loop_spec_v2.md`
- `notes/state_value_catalog.md`

---

## Inputs

- `logical_node_id`
- `candidate_root_version_id`
- required cutover scope
- current authoritative lineage selector
- cutover approval policy

---

## Required state

- candidate lineage exists and is durable
- authoritative lineage exists and is queryable
- required rebuilt scope can be enumerated
- unresolved merge conflicts and user gates are queryable

---

## Outputs

- `CutoverResult(status = "cutover_complete" | "not_ready" | "paused_for_user" | "rejected")`

Optional outputs:

- authoritative scope change summary
- superseded scope summary

---

## Durable writes

- cutover precheck event
- lineage authority selector updates
- supersession updates for replaced lineage
- cutover-completed event
- pause event if approval is required

---

## Decision algorithm

```text
function finalize_lineage_cutover(logical_node_id, candidate_root_version_id):
  candidate_scope = get_required_cutover_scope(candidate_root_version_id)
  authoritative_scope = get_current_authoritative_scope(logical_node_id)

  record_cutover_precheck(logical_node_id, candidate_root_version_id, candidate_scope)

  if not scope_is_stable(candidate_scope):
    return CutoverResult(status = "not_ready")

  if has_unresolved_merge_conflicts(candidate_scope):
    return CutoverResult(status = "rejected")

  if has_unresolved_user_gate(candidate_scope):
    pause_for_user(candidate_root_version_id, reason = "cutover_approval_required")
    return CutoverResult(status = "paused_for_user")

  begin_transaction()
  mark_candidate_scope_authoritative(candidate_scope)
  mark_replaced_scope_superseded(authoritative_scope)
  persist_cutover_completed(logical_node_id, candidate_root_version_id, candidate_scope)
  commit_transaction()

  return CutoverResult(status = "cutover_complete")
```

---

## Cutover scope rule

Recommended default scope:

- upstream lineage cutover

That means the changed node, required descendants, and required rebuilt ancestors must all be stable before authority transfer.

Local success alone is insufficient by default.

---

## Failure paths

### Candidate scope not stable

- do not cut over
- old lineage remains authoritative

### Merge conflict unresolved

- reject cutover
- preserve candidate lineage as non-authoritative

### User approval required

- pause at pre-cutover boundary
- do not mutate authority selectors yet

### Transaction failure during authority switch

- rollback selector changes
- preserve prior authority

---

## Pause/recovery behavior

- user-gated cutover should be resumable from the same candidate scope
- failed cutover transaction must not leave split authority

---

## CLI-visible expectations

Operators should be able to inspect:

- current authoritative version
- latest candidate version
- whether cutover is ready, blocked, paused, or complete
- why cutover was denied or paused

---

## Open questions

- whether first implementation should support bounded local cutover scopes at all
- whether merge-to-parent and merge-to-base approvals should be modeled as separate gates from lineage-authority cutover

---

## Pseudotests

### `does_not_cut_over_when_required_scope_is_incomplete`

Given:

- candidate root is rebuilt
- required ancestor rebuild is incomplete

Expect:

- cutover returns `not_ready`
- old lineage remains authoritative

### `pauses_when_cutover_requires_user_approval`

Given:

- candidate scope is stable
- approval policy requires user signoff

Expect:

- cutover pauses for user
- no authority selector changes occur

### `marks_old_scope_superseded_only_after_successful_authority_switch`

Given:

- cutover succeeds

Expect:

- candidate becomes authoritative
- replaced scope becomes superseded afterward
