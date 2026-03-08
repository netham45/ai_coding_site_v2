# Flow G: Rectify After Change

Sources:

- `notes/runtime_pseudocode_plan.md`
- `notes/git_rectification_spec_v2.md`
- `notes/cutover_policy_note.md`

## Scenario

`task_greeting_v1` changes and requires upstream rectification.

## Full task flow

### Step 1: create candidate superseding version

```json
{
  "status": "OK",
  "supersedes": "task_greeting_v1",
  "new_node_version_id": "task_greeting_v2",
  "authoritative_cutover": "pending_upstream"
}
```

### Step 2: compile candidate workflow

`task_greeting_v2` becomes a non-authoritative candidate lineage.

### Step 3: run rebuilt changed node

Candidate child task path:

1. `research_context`
2. leaf-local execution task
3. `validate_node`
4. `review_node`
5. `test_node`
6. `update_provenance`
7. `build_node_docs`
8. `finalize_node`

### Step 4: create candidate parent lineage

```json
{
  "status": "OK",
  "supersedes": "plan_v1",
  "new_node_version_id": "plan_v2",
  "reason": "upstream_rectification_from_task_greeting_v2"
}
```

### Step 5: rectify parent from seed

Parent candidate task path:

1. `rectify_node_from_seed`
2. `validate_node`
3. `review_node`
4. `test_node`
5. `update_provenance`
6. `build_node_docs`
7. `finalize_node`

Within `rectify_node_from_seed` the parent does:

1. reset to seed
2. merge current child finals in deterministic order
3. run parent-local reconcile

### Step 6: cut over only after stable upstream path

```json
{
  "status": "OK",
  "cutover_scope": "upstream_lineage",
  "new_authoritative_versions": [
    "task_greeting_v2",
    "plan_v2"
  ],
  "superseded_versions": [
    "task_greeting_v1",
    "plan_v1"
  ]
}
```

## Logic issues exposed

1. Active old-version run handling is still not fully folded into the canonical specs.
2. The exact boundary between `rectify_node_from_seed` and `rectify_upstream` is still somewhat high-level.

