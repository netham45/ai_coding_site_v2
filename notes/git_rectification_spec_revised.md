# Git Rectification Spec

## Purpose

This document defines how a node subtree is regenerated and how parent lineage is rebuilt upward to the top node.

Rectification is a structured rebuild process centered on resetting to seed and re-merging current child finals.

---

## 1. Core principle

When a node changes, the system should:

1. create a new node version
2. compile a new immutable workflow snapshot for that version
3. regenerate the affected subtree
4. rebuild each ancestor from its seed commit
5. re-merge all current child finals at each ancestor layer
6. rerun reconciliation, hooks, validation, review, and docs at each rebuilt layer

This is a selective rebuild pipeline from the changed subtree upward.

Any node whose dependencies are satisfied should be eligible to process immediately. Concurrency is expected across siblings and independent subtrees.

---

## 2. Branch model

Each node version is associated with one logical branch identity.

Recommended naming is tier/kind-driven rather than tied to a hardcoded hierarchy.

Example patterns:

- `tier/<tier>/<kind>/<slug>__<node_id>`
- `root/<slug>__<node_id>/<child_kind>/<child_slug>__<node_id>`

The exact naming scheme may vary, but it must be deterministic and derivable from node metadata.

Each active branch record must include:

- `seed_commit_sha`
- `final_commit_sha`
- `active_head_sha`
- `branch_generation_number`

### Seed commit

The reset anchor for rebuilding that node. In practice this is the state the node should start from before re-merging its current child set and rerunning node-local work.

### Final commit

The last successful completed output for that node version.

---

## 3. Merge model

Parent nodes do not passively inherit child state. They actively reconstruct themselves.

For any node with children, finalization should follow this process:

1. reset branch to seed commit
2. merge all current child final commits in deterministic order
3. run node-local reconciliation subtasks
4. run hooks
5. run validation
6. run review
7. build node documentation
8. commit final node state

This must apply both during initial generation and during rectification.

A top node should not automatically merge back into base unless that behavior is explicitly enabled. User-gated merge-to-base must be supported.

---

## 4. Deterministic child merge ordering

Child merge order must be replayable.

Recommended precedence:

1. explicit sibling dependency order
2. explicit child ordinal set in parent layout
3. creation timestamp
4. node ID as final tiebreaker

The chosen order must be persisted in merge metadata.

---

## 5. Example tree

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

If `PL2_2` is regenerated, the system should:

### Regenerate directly

- `PL2_2`
- `T2_2_1`
- `T2_2_2`
- `T2_2_3`

### Rebuild upward

- `P2`
- `E`

### Reuse current final outputs from siblings

- `PL2_1`
- `PL2_3`
- `P1`
- `P3`

---

## 6. Step-by-step example

### Step 1: supersede the changed plan

Create a new node version for `PL2_2`.

Persist:

- old plan version ID
- new plan version ID
- trigger reason
- source definition hash
- override set hash
- compiled workflow ID

### Step 2: supersede descendant tasks

Create new node versions for:

- `T2_2_1`
- `T2_2_2`
- `T2_2_3`

Each gets a newly compiled immutable workflow snapshot.

### Step 3: regenerate each task from seed

For each task child:

1. checkout task branch
2. hard reset to task seed commit
3. execute compiled workflow
4. run hooks
5. validate
6. review
7. build docs
8. commit new task final

### Step 4: rebuild the changed plan

On `PL2_2` branch:

1. hard reset to `PL2_2.seed_commit_sha`
2. merge final commits from the three regenerated tasks in deterministic order
3. run plan-local reconcile subtasks
4. run hooks
5. validate
6. review
7. rebuild plan docs
8. commit new `PL2_2.final_commit_sha`

### Step 5: rebuild parent node

On `P2` branch:

1. hard reset to `P2.seed_commit_sha`
2. merge `PL2_1.final(current)`
3. merge `PL2_2.final(new)`
4. merge `PL2_3.final(current)`
5. run node-local reconcile subtasks
6. run hooks
7. validate
8. review
9. rebuild docs
10. commit new `P2.final_commit_sha`

### Step 6: rebuild the top node

On `E` branch:

1. hard reset to `E.seed_commit_sha`
2. merge `P1.final(current)`
3. merge `P2.final(new)`
4. merge `P3.final(current)`
5. run top-node reconcile subtasks
6. run hooks
7. validate
8. review
9. rebuild docs
10. commit new `E.final_commit_sha`
11. if merge-to-base is enabled and not user-gated, merge into base
12. otherwise pause for explicit user approval

---

## 7. Conflict handling

Conflict policy:

1. attempt deterministic child merges in order
2. if merge is clean, continue
3. if merge conflicts occur, transition node into reconcile stage
4. execute node-local conflict resolution subtasks
5. if conflicts are resolved, continue pipeline
6. if conflicts remain unresolved, fail to parent

Every conflict event should persist:

- parent node ID
- conflicting child node IDs
- merge order position
- files conflicted
- merge base SHAs
- reconcile summary
- final resolution status

---

## 8. User gating and pause flags

Tasks and subtasks may define:

- `block_on_user_flag: <flag_name>`
- summary text or summary prompt for the pause condition

Behavior:

1. current subtask completes
2. cursor advances
3. runtime checks whether the next step is gated by a flag
4. if gated, node transitions to paused-for-user instead of executing the next step
5. a summary is recorded for the user

This mechanism should be usable for user-gated merge-to-parent and merge-to-base behaviors.

---

## 9. Upstream rebuild algorithm

```python
def regenerate_node_and_rectify_upstream(node_version_id):
    new_version = create_superseding_node_version(node_version_id)
    regenerate_subtree(new_version.id)

    for ancestor_id in get_ancestors_to_root(new_version.id):
        rectify_node_from_seed(ancestor_id)


def regenerate_subtree(node_version_id):
    children = get_children(node_version_id)
    for child in children:
        child_new_version = create_superseding_node_version(child.id)
        regenerate_subtree(child_new_version.id)
    rectify_node_from_seed(node_version_id)


def rectify_node_from_seed(node_version_id):
    branch = get_branch(node_version_id)
    checkout(branch.branch_name)
    hard_reset(branch.seed_commit_sha)

    for child in get_children_in_merge_order(node_version_id):
        merge(get_current_final_commit(child.id))
        record_merge_event(node_version_id, child.id)

    run_node_reconcile_subtasks(node_version_id)
    run_hooks(node_version_id)
    run_validation(node_version_id)
    run_review(node_version_id)
    build_node_docs(node_version_id)
    finalize_node_commit(node_version_id)
```

---

## 10. Git metadata that must be persisted

For every rebuild and merge, persist:

- node version ID
- branch name
- seed commit
- head before reset
- head after reset
- child commit SHAs merged
- merge order
- conflict events
- final commit SHA
- rebuild trigger reason
- parent lineage impacted

This data is required for CLI introspection and auditability.

---

## 11. Required git-related CLI operations

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
- `ai-tool merge-events show --node <id>`

---

## 12. Operational rule

A node branch must always be reproducible from:

- seed commit
- current child finals
- compiled workflow
- hooks
- validation and review outputs

If it is not, the system is carrying hidden state and is violating the model.

