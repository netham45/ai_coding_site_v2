# Git Rectification Spec V2

## Purpose

This document defines the canonical rebuild and rectification model for node branches, subtree regeneration, ancestor rebuilds, merge ordering, conflict handling, and supersession cutover.

V2 expands the prior git spec by:

- aligning rebuild behavior with the v2 lifecycle and runtime model
- clarifying deterministic merge and rebuild rules
- clarifying conflict handling and audit expectations
- clarifying cutover timing for superseding lineages
- clarifying how rectification interacts with quality gates, docs, and provenance

Rectification is a structured rebuild process centered on:

- immutable compiled workflows
- seed commits
- current child final commits
- deterministic merge order
- node-local reconciliation
- upstream reconstruction

---

## 1. Core principle

When a node changes, the system should:

1. create a new node version
2. compile a new immutable workflow snapshot for that version
3. regenerate the affected subtree as required
4. rebuild each required ancestor from its seed commit
5. re-merge current child final commits at each ancestor layer
6. rerun quality gates, docs, and provenance at each rebuilt layer
7. cut over only after the rebuilt lineage is stable enough to become authoritative

This is a selective rebuild pipeline from the changed subtree upward.

---

## 2. Branch model

Each node version is associated with one logical branch identity.

Recommended branch naming should be deterministic and derivable from node metadata.

Current implementation rule:

- `tier/<tier>/<kind>/<title-slug>__<logical_node_id_hex>/v<version_number>`

Where:

- `tier` and `kind` are normalized to lowercase dash-separated path components
- `title-slug` is a lowercase dash-separated slug derived from the node-version title
- `logical_node_id_hex` is the stable logical node UUID with dashes removed
- `version_number` matches the durable branch generation number for the node version

This freezes one canonical first-pass naming rule for implementation and testing.

Each active branch record must include:

- `seed_commit_sha`
- `final_commit_sha`
- `active_head_sha` if tracked operationally
- `branch_generation_number`

Implementation staging note:

- the current implementation persists `active_branch_name`, `seed_commit_sha`, `final_commit_sha`, and `branch_generation_number`
- `active_head_sha` remains deferred until live git/session orchestration phases actually track working head state durably

---

## 3. Seed and final commit rules

### Seed commit

The reset anchor for rebuilding the node.

It represents the state the node should start from before:

- merging current child finals
- rerunning node-local reconcile work
- rerunning quality gates

### Final commit

The last successful completed output for that node version.

It should be recorded only after:

1. reconciliation succeeds
2. validation succeeds
3. review succeeds
4. testing succeeds unless policy allows otherwise
5. provenance refresh succeeds
6. docs build succeeds
7. finalization succeeds

Implementation staging note:

- the current implementation supports durable seed/final recording and immutable commit anchors per node version
- it now also exposes a runtime-owned live repo bootstrap path so per-version repos can be created through the daemon/CLI surface before merge/finalize execution
- it now also supports a real live finalize commit path for the parent merge/finalize flow
- it does not yet enforce the full rebuild-driven quality-gate/finalization pipeline before `final_commit_sha` is recorded; that stronger guard lands with the later rebuild/runtime git slices

---

## 4. Canonical rectification order

The default built-in rectification order is:

1. reset branch to seed
2. merge current child finals in deterministic order
3. reconcile merged output
4. validation
5. review
6. testing
7. provenance update
8. docs build
9. finalize node

This must align with the lifecycle and runtime v2 specs.

---

## 5. Deterministic child merge ordering

Child merge order must be replayable.

Recommended precedence:

1. explicit sibling dependency order
2. explicit child ordinal in parent layout
3. child creation timestamp
4. child node ID as final tiebreaker

The chosen order must be persisted in merge metadata.

Implementation staging note:

- the daemon now exposes a runtime-owned repo bootstrap surface for per-version repos before live merge/finalize work begins
- the current implementation now computes deterministic child merge order from durable sibling dependencies, child ordinals, child-edge creation time, and logical child id
- merge execution in this phase now shells out to live `git fetch` and `git merge --no-ff --no-edit` against the per-version runtime repos
- the daemon records replayable `merge_events`, persists `merge_conflicts` on conflict, and writes the derived parent reconcile context into the active run cursor

---

## 6. Child merge model

Parent nodes do not passively inherit child state. They actively reconstruct themselves.

For a node with children, rectification/finalization should follow:

1. reset branch to seed commit
2. merge all current child final commits in deterministic order
3. run node-local reconcile subtasks
4. run validation
5. run review
6. run testing
7. refresh provenance
8. build docs
9. commit final node state

This applies both during:

- initial generation of a parent after children complete
- rectification after a descendant change

---

## 7. Example tree behavior

Assume a default ladder:

- `E`
  - `P1`
  - `P2`
    - `PL2_1`
    - `PL2_2`
      - `T2_2_1`
      - `T2_2_2`
      - `T2_2_3`
    - `PL2_3`
  - `P3`

If `PL2_2` changes, the system should:

### Regenerate directly

- `PL2_2`
- its required descendants

### Rebuild upward

- `P2`
- `E`

### Reuse current sibling finals

- `PL2_1`
- `PL2_3`
- `P1`
- `P3`

Rule:

- siblings are reused by current final commit unless their own definitions or inputs changed

---

## 8. Regeneration flow

When a node changes:

1. create a superseding node version
2. compile a new immutable workflow snapshot
3. create superseding versions for required descendants
4. execute regeneration for those descendants
5. rectify the changed node from seed
6. rectify ancestors upward
7. cut over only after required rebuilt lineage is stable

This must be auditable through:

- `rebuild_events`
- `merge_events`
- `merge_conflicts`
- node version lineage

---

## 9. Rectification pseudocode

```python
def regenerate_node_and_rectify_upstream(node_version_id):
    new_version = create_superseding_node_version(node_version_id)
    regenerate_required_descendants(new_version.id)
    rectify_node_from_seed(new_version.id)

    for ancestor_id in get_ancestors_to_root(new_version.id):
        rectify_node_from_seed(ancestor_id)

    finalize_lineage_cutover(new_version.id)


def rectify_node_from_seed(node_version_id):
    branch = get_branch(node_version_id)
    checkout(branch.name)
    hard_reset(branch.seed_commit_sha)

    for child in get_children_in_merge_order(node_version_id):
        merge(get_current_final_commit(child.id))
        record_merge_event(node_version_id, child.id)

    run_node_reconcile_subtasks(node_version_id)
    run_validation(node_version_id)
    run_review(node_version_id)
    run_testing(node_version_id)
    update_provenance(node_version_id)
    build_node_docs(node_version_id)
    finalize_node_commit(node_version_id)
```

The implementation must expand these helpers into durable runtime transitions and failure handling.

---

## 10. Conflict handling

Conflict policy:

1. attempt deterministic child merges in order
2. if merge is clean, continue
3. if merge conflicts occur, persist a conflict record
4. transition into reconcile/conflict-resolution stage
5. if conflicts are resolved, continue the quality-gate pipeline
6. if conflicts remain unresolved, fail to parent or pause for user according to policy

Every conflict event should persist:

- parent node version
- child node version
- merge order position
- files conflicted
- merge base SHA if available
- resolution summary
- final resolution status

---

## 11. User gating and merge approval

Rectification and merge-to-parent/base may be user-gated.

Behavior:

1. current rectification stage completes
2. a summary is recorded
3. the node transitions to `PAUSED_FOR_USER`
4. explicit approval is required before merge continuation

This mechanism should support:

- user-gated merge to parent
- user-gated merge to base
- user review before accepting rebuilt output

---

## 12. Upstream rectification rule

When a rebuilt child changes a parent's effective output:

1. the parent must rebuild from seed
2. the parent must re-merge all current child finals
3. the parent must rerun its own quality gates, provenance, docs, and finalization

This process repeats upward until:

- the top node is rebuilt, or
- policy explicitly limits the rebuild scope

Any ancestor rebuild must use current child finals, not stale in-memory assumptions.

---

## 13. Supersession and cutover timing

The old lineage should not be marked fully superseded until the new required lineage is stable.

At minimum, cutover policy must define:

- whether the changed node must finish first
- whether all required descendants must finish first
- whether all required ancestors must finish first
- what happens to active runs on old versions

Recommended default:

- cut over only after the changed node and required upstream rebuild path complete successfully

If rebuild fails before cutover:

- the old lineage remains authoritative
- failure should be inspectable through rebuild and run history

---

## 14. Top-node merge-to-base rule

A top node should not automatically merge back into base unless that behavior is explicitly enabled.

The system must support:

- auto-merge to base
- user-gated merge to base
- no automatic merge to base

The chosen behavior must be visible through policy and CLI.

---

## 15. Git metadata that must be persisted

For every rebuild and merge, persist:

- node version ID
- branch name
- branch generation number
- seed commit
- head before reset
- head after reset
- child commit SHAs merged
- merge order
- conflict events
- final commit SHA
- rebuild trigger reason
- parent lineage impacted

If this data is not persisted, rebuilds become less auditable and less reproducible.

---

## 16. Required git-related CLI operations

Suggested commands:

- `ai-tool git branch show --node <id>`
- `ai-tool git seed show --node <id>`
- `ai-tool git final show --node <id>`
- `ai-tool git reset-node-to-seed --node <id>`
- `ai-tool git merge-current-children --node <id> --ordered`
- `ai-tool git finalize-node --node <id>`
- `ai-tool git lineage show --node <id>`
- `ai-tool node regenerate --node <id>`
- `ai-tool node rectify-upstream --node <id>`
- `ai-tool node rebuild-coordination --node <id> --scope subtree|upstream`
- `ai-tool node version cutover-readiness --version <id>`
- `ai-tool merge-events show --node <id>`
- `ai-tool merge-conflicts show --node <id>`
- `ai-tool rebuild show --node <id>`

---

## 17. Operational rule

A node branch must always be reproducible from:

- seed commit
- current child final commits
- compiled workflow
- review/testing/docs/provenance policies that affected execution
- validation, review, and testing outputs
- finalization history

If it is not, the system is carrying hidden state and is violating the model.

---

## 18. V2 closure notes

This V2 git/rectification spec resolves or reduces the following prior gaps:

- clearer rectification ordering
- clearer conflict handling
- clearer cutover timing expectations
- clearer alignment with lifecycle/runtime quality gates

Remaining follow-on work still needed:

- decide the final canonical branch naming pattern
- further refine active old-run behavior during supersession
- rerun the gap matrix against the completed v2 core spec set
Implementation note: the current codebase now persists staged rebuild history and deterministic candidate rectification anchors in the database. Real working-tree `git reset` / merge execution is still deferred, but rebuild lineage, merge ordering, cutover gating, explicit rebuild-coordination inspection, and blocked-attempt audit are now durable and inspectable.
