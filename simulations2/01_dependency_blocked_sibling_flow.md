# Dependency-Blocked Sibling Flow

Sources:

- `notes/node_lifecycle_spec_v2.md`
- `notes/invalid_dependency_graph_handling.md`
- `notes/child_materialization_and_scheduling.md`
- `notes/database_schema_spec_v2.md`
- `notes/cli_surface_spec_v2.md`
- `notes/yaml_schemas_spec_v2.md`

## Scenario

A `plan` node generates two child `task` nodes:

- `task_a_v1`
- `task_b_v1`

`task_b_v1` depends on `task_a_v1`.

This is the canonical non-cyclic sibling wait path.

## Assumptions

Assumed built-in source paths because the notes define families but not one frozen on-disk library layout:

- built-in node definition: `builtin/nodes/plan.yaml`
- built-in task definitions:
  - `builtin/tasks/research_context.yaml`
  - `builtin/tasks/generate_child_layout.yaml`
  - `builtin/tasks/review_child_layout.yaml`
  - `builtin/tasks/spawn_children.yaml`
  - `builtin/tasks/wait_for_children.yaml`
  - `builtin/tasks/reconcile_children.yaml`
  - `builtin/tasks/validate_node.yaml`
  - `builtin/tasks/review_node.yaml`
  - `builtin/tasks/test_node.yaml`
  - `builtin/tasks/update_provenance.yaml`
  - `builtin/tasks/build_node_docs.yaml`
  - `builtin/tasks/finalize_node.yaml`

Assumed project-local request file:

- `.ai/requests/plan_with_dependency.yaml`

## Input YAML

### Request file read

```yaml
request:
  title: Plan with dependent sibling tasks
  prompt: >
    Create two child tasks. Task A generates shared parsed config output.
    Task B consumes Task A output and builds the final greeting artifact.
  target_kind: plan
```

### Generated layout file read later during validation/materialization

```yaml
layout_definition:
  children:
    - id: task_a
      kind: task
      tier: task
      name: Parse config task
      dependencies: []
      acceptance:
        - parsed config output exists
    - id: task_b
      kind: task
      tier: task
      name: Build greeting task
      dependencies:
        - task_a
      acceptance:
        - greeting output exists
```

## CLI sequence

### 1. Create top-level plan node

```text
ai-tool node create \
  --kind plan \
  --title "Plan with dependent sibling tasks" \
  --file .ai/requests/plan_with_dependency.yaml
```

### 2. Inspect compiled workflow

```text
ai-tool workflow show --node plan_v1
ai-tool workflow sources --node plan_v1
```

### 3. Start the plan run

```text
ai-tool node run start --node plan_v1
```

### 4. Generate and validate layout

```text
ai-tool layout generate --node plan_v1
ai-tool layout show --node plan_v1
ai-tool layout validate --node plan_v1
```

### 5. Materialize and inspect dependency state

```text
ai-tool node children --node plan_v1 --versions
ai-tool node dependencies --node task_b_v1
ai-tool node dependency-status --node task_b_v1
ai-tool node blockers --node task_b_v1
```

### 6. Start ready child only

```text
ai-tool node run start --node task_a_v1
ai-tool node run show --node task_a_v1
ai-tool node run show --node task_b_v1
```

### 7. After `task_a_v1` completes, re-check readiness

```text
ai-tool node dependency-status --node task_b_v1
ai-tool node blockers --node task_b_v1
ai-tool node run start --node task_b_v1
```

## YAML and source reads

### During `node create`

Daemon reads:

1. `.ai/requests/plan_with_dependency.yaml`
2. `builtin/nodes/plan.yaml`
3. built-in task YAML files referenced by the `plan` node definition
4. any applicable project-local policy files under `.ai/policies/`
5. any applicable overrides under `.ai/overrides/nodes/` and `.ai/overrides/tasks/`

### During `layout validate`

Daemon reads:

1. materialized layout file for `plan_v1`
2. parent node definition constraints
3. dependency validation rules

### During run admission for `task_b_v1`

Daemon reads:

1. authoritative current version mapping for `task_a`
2. `node_dependencies` for `task_b_v1`
3. lifecycle state for `task_a_v1`
4. `node_runs` and `node_run_state` for `task_b_v1`

## Relation checks

### Creation and compile checks

1. request `target_kind=plan` matches a known `node_definition`
2. parentless top-level creation allowed by parent constraints
3. selected task definitions all exist
4. resolved YAML validates

### Layout checks

1. child IDs `task_a` and `task_b` are unique
2. child kinds `task` are allowed under parent `plan`
3. dependency target `task_a` exists in the same child set
4. dependency type is allowed sibling dependency
5. no self-dependency
6. no cycle

### Materialization checks

1. no existing child set conflicts with this authoritative layout hash
2. each child gets at most one parent
3. dependency edge resolves from `task_b_v1` to `task_a_v1`

### Run admission checks for `task_b_v1`

1. `task_b_v1` exists
2. compiled workflow exists
3. no incompatible active run already exists
4. dependency target is authoritative `task_a_v1`
5. required dependency state is `COMPLETE`
6. if dependency not complete, child must not start

## Durable DB writes

### Top-level create and compile

1. `node_versions`
   - insert `plan_v1`
2. `logical_node_current_versions`
   - insert logical node mapping
   - `authoritative_node_version_id = plan_v1`
   - `latest_created_node_version_id = plan_v1`
3. `source_documents`
   - insert one row per built-in or project-local YAML file used
4. `compiled_workflows`
   - insert `cw_plan_v1`
5. `compiled_workflow_sources`
   - insert one row per `(cw_plan_v1, source_document_id)`
6. `compiled_tasks`
   - insert ordered plan tasks
7. `compiled_subtasks`
   - insert ordered subtasks for each compiled task
8. `compiled_subtask_dependencies`
   - insert any subtask-level dependency edges
9. `compiled_subtask_checks`
   - insert validation/review/test checks
10. `workflow_events`
   - insert compile completion event

### Plan run start

1. `node_runs`
   - insert `run_plan_v1_1`
2. `node_run_state`
   - insert row with:
     - `lifecycle_state = RUNNING`
     - first `current_task_id`
     - first `current_compiled_subtask_id`
3. `sessions`
   - insert primary session for the run
4. `session_events`
   - insert `bound` and `attached`
5. `workflow_events`
   - insert run-admitted event

### Layout generation and validation

1. `subtask_attempts`
   - insert attempts for plan subtasks that generate layout
2. `prompts`
   - insert prompt used to generate child layout
3. `summaries`
   - insert plan summary describing child design
4. `validation_results`
   - insert successful dependency validation result for the layout-checking subtask

### Child materialization

1. `node_versions`
   - insert `task_a_v1`
   - insert `task_b_v1`
2. `logical_node_current_versions`
   - insert authoritative mappings for logical `task_a` and logical `task_b`
3. `node_children`
   - insert `(plan_v1, task_a_v1, layout_generated, ordinal=1)`
   - insert `(plan_v1, task_b_v1, layout_generated, ordinal=2)`
4. `parent_child_authority`
   - upsert `plan_v1 -> layout_authoritative`
5. `node_dependencies`
   - insert one row:
     - `node_version_id = task_b_v1`
     - `depends_on_node_version_id = task_a_v1`
     - `dependency_type = sibling`
     - `required_state = COMPLETE`
6. `node_version_lineage`
   - insert authoritative lineage edges:
     - `(plan_v1, task_a_v1, authoritative)`
     - `(plan_v1, task_b_v1, authoritative)`
7. `source_documents`
   - insert generated layout source if modeled as a source document
8. `summaries`
   - insert materialization summary for parent
9. `workflow_events`
   - insert child materialization event

### Child compile rows

For each child:

1. `compiled_workflows`
2. `compiled_workflow_sources`
3. `compiled_tasks`
4. `compiled_subtasks`
5. `compiled_subtask_checks`

### Scheduling classification

1. `workflow_events`
   - insert scheduler classification event for `task_a_v1` as ready
   - insert scheduler classification event for `task_b_v1` as blocked
2. no `node_runs` row yet for `task_b_v1`

### `task_a_v1` run start and completion

1. `node_runs`
   - insert `run_task_a_v1_1`
2. `node_run_state`
   - insert then update through task progression
3. `subtask_attempts`
   - insert rows for each child subtask attempt
4. `prompts`
   - insert implementation/review/test prompts as needed
5. `validation_results`
6. `review_results`
7. `test_results`
8. `summaries`
   - insert child summary
9. `node_docs`
   - insert built docs rows if docs task runs
10. `node_versions`
   - update `final_commit_sha` for `task_a_v1`
11. `node_run_state`
   - update `lifecycle_state` to `COMPLETE`
12. `node_runs`
   - update `run_status` to `COMPLETE`

### Unblock and `task_b_v1` run start

1. `workflow_events`
   - insert `dependency_unblocked`
2. `node_runs`
   - insert `run_task_b_v1_1`
3. `node_run_state`
   - insert running cursor row

## State transitions

### Parent

- `plan_v1: READY -> RUNNING -> WAITING_ON_CHILDREN -> RUNNING`

### Child A

- `task_a_v1: COMPILED -> READY -> RUNNING -> COMPLETE`

### Child B

- `task_b_v1: COMPILED -> WAITING_ON_SIBLING_DEPENDENCY -> READY -> RUNNING -> COMPLETE`

## Inspectable outputs

### Before `task_a_v1` completes

`ai-tool node blockers --node task_b_v1`

```yaml
node_version_id: task_b_v1
lifecycle_state: WAITING_ON_SIBLING_DEPENDENCY
blockers:
  - blocker_type: sibling_dependency
    target_node_version_id: task_a_v1
    target_required_state: COMPLETE
    target_current_state: RUNNING
```

### After `task_a_v1` completes

`ai-tool node dependency-status --node task_b_v1`

```yaml
node_version_id: task_b_v1
dependencies:
  - depends_on_node_version_id: task_a_v1
    required_state: COMPLETE
    current_state: COMPLETE
    satisfied: true
overall_status: ready
```

## Result

This simulation shows the normal blocked-sibling path without any knot:

- dependency is validated before materialization
- blocked child is visible and queryable
- parent waits without guessing
- child unblocks only when the authoritative dependency reaches `COMPLETE`

## Hole still visible

The notes still do not freeze whether parent surfaces should simultaneously expose both:

- broad parent `WAITING_ON_CHILDREN`
- specific child-level `WAITING_ON_SIBLING_DEPENDENCY`

The simulation assumes both are visible.
