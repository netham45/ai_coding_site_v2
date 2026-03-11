# Module: `rectify_node_from_seed(...)`

## Purpose

Rebuild one node version from its seed commit by replaying child merges for that candidate lineage, then rerunning reconcile and quality-gate stages until a new final commit is produced or failure stops the path.

---

## Source notes

Primary:

- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/runtime/cutover_policy_note.md`

Supporting:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/provenance/provenance_identity_strategy.md`

---

## Inputs

- `node_version_id`
- branch metadata
- seed commit
- authoritative child final commits
- reconcile and quality-gate workflow for the node

---

## Required state

- node version exists and is in candidate or rebuild context
- seed commit is known
- child merge replay order is derivable for the rebuilt lineage
- authoritative child finals are queryable

---

## Outputs

- updated branch state after reset and child merges
- reconciliation and quality-gate results
- final commit on success
- merge conflict or failure records on failure

---

## Durable writes

- rectification event
- merge events in deterministic order
- merge conflict records where applicable
- validation, review, testing, provenance, and docs results
- final commit metadata on success

---

## Happy path

```text
function rectify_node_from_seed(node_version_id):
  branch = load_branch_metadata(node_version_id)
  child_results = collect_child_results(node_version_id)

  if any(result.reconcile_status == "invalid_authority" for result in child_results.snapshot):
    return RectificationResult(status = "invalid_child_authority")

  checkout_branch(branch.name)
  hard_reset_to_seed(branch.seed_commit_sha)
  record_rectification_started(node_version_id, branch.seed_commit_sha)

  merge_order = get_children_in_deterministic_merge_order(node_version_id, child_results.snapshot)

  for child in merge_order:
    merge_result = merge_child_final_commit(node_version_id, child.final_commit_sha)
    record_merge_event(node_version_id, child.child_id, merge_result)
    if merge_result.status == "conflict":
      record_merge_conflict(node_version_id, child.child_id, merge_result.conflict_payload)
      return RectificationResult(status = "merge_conflict", child_id = child.child_id)

  reconcile_result = run_node_reconcile_subtasks(node_version_id)
  if reconcile_result.status != "ok":
    return RectificationResult(status = "reconcile_failed")

  validation = run_validation(node_version_id)
  if validation.status != "ok":
    return RectificationResult(status = "validation_failed")

  review = run_review(node_version_id)
  if review.status == "pause":
    return RectificationResult(status = "paused_for_user")
  if review.status != "ok":
    return RectificationResult(status = "review_failed")

  testing = run_testing(node_version_id)
  if testing.status != "ok":
    return RectificationResult(status = "testing_failed")

  provenance = update_provenance(node_version_id)
  if provenance.status != "ok":
    return RectificationResult(status = "provenance_failed")

  docs = build_node_docs(node_version_id)
  if docs.status != "ok":
    return RectificationResult(status = "docs_failed")

  final_commit = finalize_node_commit(node_version_id)
  record_final_commit(node_version_id, final_commit.sha)
  return RectificationResult(status = "ok", final_commit_sha = final_commit.sha)
```

---

## Ordering rules

- The authoritative live parent lineage now consumes already-applied incremental child merge history during final reconcile and does not synthesize a second final-stage merge sequence.
- Candidate-version rectification still needs a replay order for the rebuilt lineage.
- Where a rebuilt lineage already has merge metadata, replay should follow that persisted order.
- Where it does not, the daemon may derive a deterministic replay order from sibling dependency order, child ordinal, creation timestamp, and child node ID.

---

## Failure paths

### Invalid child authority

- stop before merging
- do not guess which child finals to use

### Merge conflict

- persist conflict record
- stop rectification until resolution path is chosen

### Quality-gate failure

- do not record final commit
- candidate lineage remains non-authoritative

### Finalization failure

- preserve prior successful stages
- no authoritative cutover occurs

---

## Cutover interaction

- successful rectification of one node does not itself guarantee authoritative cutover
- cutover occurs only after the required rebuilt lineage scope is stable
- old lineage remains authoritative until that point

---

## Provenance interaction

- provenance refresh should update entity identity using deterministic matches when possible and explicit-confidence inference when necessary
- provenance failure should block finalization if docs and auditability depend on it

---

## CLI-visible expectations

Operators should be able to inspect:

- seed commit used
- merge order used
- child finals merged
- merge conflicts encountered
- current rectification stage and latest blocking failure

---

## Open questions

- whether merge conflict resolution should occur as dedicated compiled subtasks or as a rectification substate outside ordinary workflow execution
- whether docs failure should always block finalization or be policy-relaxable

---

## Pseudotests

### `rebuilds_from_seed_then_merges_authoritative_child_finals_in_replay_order`

Given:

- node has multiple authoritative child finals

Expect:

- branch resets to seed
- children merge in the replay order chosen for the rebuilt lineage

### `stops_on_merge_conflict_and_records_conflict`

Given:

- one child merge conflicts

Expect:

- conflict is recorded
- later quality gates do not run

### `does_not_cut_over_on_local_success_alone`

Given:

- one rebuilt node rectifies successfully
- upstream lineage is not yet stable

Expect:

- node remains candidate until lineage cutover conditions are satisfied
