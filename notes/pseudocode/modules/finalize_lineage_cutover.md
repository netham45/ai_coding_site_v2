# Module: `finalize_lineage_cutover(...)`

## Purpose

Transfer authority from an old authoritative lineage to a stable candidate lineage only after the required rebuilt scope is complete, valid, and approved where necessary.

---

## Source notes

Primary:

- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/specs/git/git_rectification_spec_v2.md`

Supporting:

- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/catalogs/vocabulary/state_value_catalog.md`

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
  candidate_scope = enumerate_required_cutover_scope(candidate_root_version_id)
  authoritative_scope = get_current_authoritative_scope(logical_node_id)

  record_cutover_precheck(logical_node_id, candidate_root_version_id, candidate_scope)

  if not scope_is_stable(candidate_scope):
    return CutoverResult(status = "not_ready")

  if authoritative_baseline_changed(candidate_scope):
    return CutoverResult(status = "not_ready")

  if candidate_replay_is_incomplete(candidate_scope):
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

`scope_is_stable(...)` should include:

- all required candidate versions exist
- all required descendants and ancestors in the enumerated scope are stable
- replay-complete status is recorded for nodes that require candidate replay
- reused children remain valid for this candidate lineage
- no scope member has been superseded

Current implementation note:

- `enumerate_required_cutover_scope(...)` now exists as a durable rebuild-backed helper
- cutover-readiness inspection now evaluates the enumerated scope instead of only the requested candidate version
- manual cutover already switches the enumerated scope together; remaining gaps are around broader real-flow proof and replay/rematerialization follow-through, not single-version readiness logic
- grouped cutover also has one narrow follow-on exception: ancestor cutover may proceed with dependency-invalidated descendant replay blockers when those descendants are explicitly waiting for post-cutover parent refresh/rematerialization instead of claiming they are already replay-complete

---

## Cutover scope rule

Recommended default scope:

- upstream lineage cutover

That means the changed node, required descendants, and required rebuilt ancestors must all be stable before authority transfer.

Local success alone is insufficient by default.

The default implementation should therefore assume:

- the candidate root is not enough
- required descendants alone are not enough
- required rebuilt ancestors up to the stopping point must also be ready

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
- which versions are inside the enumerated required scope
- whether replay is incomplete versus conflict-blocked versus drift-blocked
- whether the candidate baseline no longer matches the current authoritative lineage

---

## Open questions

- whether first implementation should support bounded local cutover scopes at all
- whether merge-to-parent and merge-to-base approvals should be modeled as separate gates from lineage-authority cutover
- whether operator override for authoritative-baseline drift should ever be allowed or always require rebuild restart

## Candidate Replay And Cutover Invariants

- Candidate replay must be evaluated against the candidate lineage, not the authoritative live parent lane.
- A candidate lineage is not `stable_for_cutover` while any required replay child is missing, invalidated, or blocked pending refresh.
- Authoritative live `merge_events` are useful audit input, but candidate replay readiness must not depend on the authoritative live lane continuing to advance.

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
