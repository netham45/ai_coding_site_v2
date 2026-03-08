# Rectification Stateful Flow

Sources:

- `notes/node_lifecycle_spec_v2.md`
- `notes/hypothetical_plan_workthrough.md`
- `notes/database_schema_spec_v2.md`
- `notes/cli_surface_spec_v2.md`

## Scenario

Leaf node `task_greeting_v1` is regenerated into `task_greeting_v2`. Parent `plan_v1` is rebuilt into candidate `plan_v2`. The simulation makes candidate lineage rows, rebuild events, merge events, and cutover writes explicit.

## Starting authoritative state

Logical-node mapping reads:

- logical `plan` -> authoritative `plan_v1`
- logical `task_parser` -> authoritative `task_parser_v1`
- logical `task_greeting` -> authoritative `task_greeting_v1`

Existing rows read:

1. `logical_node_current_versions`
2. `node_versions`
3. `node_children`
4. `node_version_lineage`
5. final commits on authoritative nodes

## CLI sequence

### Regenerate changed child

```text
ai-tool node regenerate --node task_greeting_v1
```

### Inspect lineage and workflow

```text
ai-tool node lineage --node task_greeting_v2
ai-tool workflow show --node task_greeting_v2
```

### Run candidate child

```text
ai-tool node run start --node task_greeting_v2
ai-tool node run show --node task_greeting_v2
```

### Inspect candidate parent lineage

```text
ai-tool node lineage --node plan_v2
ai-tool tree show --node plan_v2
```

### Inspect cutover after rebuild

```text
ai-tool node lineage --node task_greeting_v2
ai-tool node lineage --node plan_v2
ai-tool tree show --node plan_v2
```

## Step 1: create candidate child version

### Relation checks

1. `task_greeting_v1` exists
2. no other candidate version already violates uniqueness assumptions
3. superseding version number increments correctly

### DB writes

1. `node_versions`
   - insert `task_greeting_v2`:
     - same `logical_node_id` as `task_greeting_v1`
     - `supersedes_node_version_id = task_greeting_v1`
     - candidate branch metadata
2. `logical_node_current_versions`
   - update only:
     - `latest_created_node_version_id = task_greeting_v2`
   - keep:
     - `authoritative_node_version_id = task_greeting_v1`
3. `rebuild_events`
   - insert:
     - `old_node_version_id = task_greeting_v1`
     - `new_node_version_id = task_greeting_v2`
     - `trigger_reason = regenerate`
4. `workflow_events`
   - insert candidate-version-created event

## Step 2: compile candidate child workflow

### Reads

1. source YAML for task node kind
2. applicable policies/overrides

### Writes

1. `compiled_workflows`
   - insert `cw_task_greeting_v2`
2. `compiled_workflow_sources`
3. `compiled_tasks`
4. `compiled_subtasks`
5. `compiled_subtask_checks`

## Step 3: run candidate child

### Writes

1. `node_runs`
   - insert `run_task_greeting_v2_1`
2. `node_run_state`
   - insert running cursor row
3. `sessions`
   - insert primary session
4. `session_events`
5. `subtask_attempts`
6. `prompts`
7. `validation_results`
8. `review_results`
9. `test_results`
10. `summaries`
11. `node_docs`
12. `node_versions`
   - update `final_commit_sha = greet222`
13. `node_run_state`
   - update `lifecycle_state = COMPLETE`
14. `node_runs`
   - update `run_status = COMPLETE`

### Important invariant

Despite successful completion:

- `logical_node_current_versions.authoritative_node_version_id` remains `task_greeting_v1`
- candidate success does not cause early cutover

## Step 4: create candidate parent version

### Reads

1. authoritative parent `plan_v1`
2. authoritative unchanged sibling `task_parser_v1`
3. candidate changed child `task_greeting_v2`

### Writes

1. `node_versions`
   - insert `plan_v2`
2. `logical_node_current_versions`
   - update only:
     - `latest_created_node_version_id = plan_v2`
   - keep authoritative `plan_v1`
3. `rebuild_events`
   - insert upstream rebuild event
4. `node_version_lineage`
   - insert candidate lineage edges:
     - `(plan_v2, task_parser_v1, candidate)`
     - `(plan_v2, task_greeting_v2, candidate)`
5. `workflow_events`
   - insert upstream candidate-created event

## Step 5: parent enters rectification

### Lifecycle write

1. `node_run_state`
   - for `plan_v2` rectify run, insert:
     - `lifecycle_state = RECTIFYING_UPSTREAM`

### Compile writes for candidate parent

1. `compiled_workflows`
2. `compiled_workflow_sources`
3. `compiled_tasks`
4. `compiled_subtasks`
5. `compiled_subtask_checks`

### Merge/reconcile writes

1. `node_runs`
   - insert rectify run for `plan_v2`
2. `subtask_attempts`
   - insert attempts for:
     - reset to seed
     - merge children
     - record merge metadata
     - reconcile
     - validate
     - review
     - run tests
     - update provenance
     - build docs
     - finalize
3. `merge_events`
   - insert for merging `task_parser_v1.final`
   - insert for merging `task_greeting_v2.final`
4. `validation_results`
5. `review_results`
6. `test_results`
7. `node_docs`
8. `node_versions`
   - update `plan_v2.final_commit_sha = plan222`
9. `node_run_state`
   - update `lifecycle_state = COMPLETE`
10. `node_runs`
   - update `run_status = COMPLETE`
11. `workflow_events`
   - insert rectify completed

## Step 6: cutover

### Relation checks before cutover

1. candidate child complete
2. candidate parent complete
3. required upstream lineage stable
4. no unresolved merge conflict rows
5. no policy block preventing cutover

### Cutover writes

1. `logical_node_current_versions`
   - for logical `task_greeting`:
     - `authoritative_node_version_id = task_greeting_v2`
   - for logical `plan`:
     - `authoritative_node_version_id = plan_v2`
2. `node_version_lineage`
   - insert authoritative lineage edges:
     - `(plan_v2, task_parser_v1, authoritative)`
     - `(plan_v2, task_greeting_v2, authoritative)`
3. `workflow_events`
   - insert `cutover_completed`
4. `node_versions`
   - older versions become historical/superseded in visible state if modeled directly through status

### Important non-write

`task_parser_v1` remains authoritative and unchanged.

## Merge-conflict variant

If merge of `task_greeting_v2.final` into `plan_v2` conflicts:

### Writes

1. `merge_events`
   - insert merge event with `had_conflict = true`
2. `merge_conflicts`
   - insert unresolved conflict record
3. `workflow_events`
   - insert `merge_conflict_unresolved`
4. `summaries`
   - insert operator summary
5. parent current state:
   - pause or failure path according to policy

### Writes that must not happen

- no update of `logical_node_current_versions.authoritative_node_version_id` for plan
- no authoritative cutover for candidate lineage

## Result

This simulation makes the full candidate-lineage model concrete:

- latest-created and authoritative versions diverge during rebuild
- candidate lineage edges are separate from authoritative lineage edges
- rectification writes merge history durably
- cutover is a final explicit write, not an implied side effect

## Hole still visible

The notes still do not freeze whether superseded versions should be marked directly in `node_versions.status` at cutover time or only inferred from current-version mappings plus lineage/history.
