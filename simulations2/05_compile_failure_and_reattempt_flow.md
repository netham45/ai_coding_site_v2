# Compile Failure And Reattempt Flow

Sources:

- `notes/compile_failure_persistence.md`
- `notes/database_schema_spec_v2.md`
- `notes/state_value_catalog.md`
- `notes/cli_surface_spec_v2.md`
- `notes/yaml_schemas_spec_v2.md`

## Scenario

The operator bootstraps a new project node, but an override points to a non-existent built-in task. Compilation fails durably. The operator fixes the override and recompiles the same node version successfully.

## Assumed source files

- request file: `.ai/requests/bootstrap.yaml`
- built-in node definition: `builtin/nodes/plan.yaml`
- project policy: `.ai/policies/project.yaml`
- project testing definition: `.ai/testing/python_default.yaml`
- bad override: `.ai/overrides/tasks/review_node.yaml`

## CLI sequence

### First compile attempt through node creation

```text
ai-tool node create \
  --kind plan \
  --title "Bootstrap greeting feature" \
  --file .ai/requests/bootstrap.yaml
```

### Inspect compile failures

```text
ai-tool workflow compile-failures --node proj_plan_v1
ai-tool node show --node proj_plan_v1
```

### Attempted run start that must fail

```text
ai-tool node run start --node proj_plan_v1
```

### Fix override and recompile

```text
ai-tool workflow compile --node proj_plan_v1
```

### Inspect successful workflow

```text
ai-tool workflow show --node proj_plan_v1
ai-tool yaml resolved --node proj_plan_v1
ai-tool node run start --node proj_plan_v1
```

## YAML reads during failed compile

1. `.ai/requests/bootstrap.yaml`
2. `builtin/nodes/plan.yaml`
3. built-in task YAML referenced by plan node
4. `.ai/policies/project.yaml`
5. `.ai/testing/python_default.yaml`
6. `.ai/overrides/tasks/review_node.yaml`

## Failed compile relation checks

1. request file exists and validates
2. node kind `plan` resolves to built-in `node_definition`
3. project policy validates as `project_policy_definition`
4. testing file validates as `testing_definition`
5. override file validates structurally as `override_definition`
6. override target resolution checks:
   - `family = task_definition`
   - `document_id = review_node_old_name`
7. no built-in or project-local task definition with ID `review_node_old_name` exists
8. compile stops in `override_resolution`

## Durable DB writes on failed attempt

### Writes that occur before failure

1. `node_versions`
   - insert `proj_plan_v1`
2. `logical_node_current_versions`
   - insert mapping for logical node
3. `source_documents`
   - insert rows for each source file read

### Failure write

1. `compile_failures`
   - insert:
     - `node_version_id = proj_plan_v1`
     - `failure_stage = override_resolution`
     - `failure_class = override_missing_target`
     - `summary = Override target task_definition/review_node_old_name was not found.`
     - `target_family = task_definition`
     - `target_id = review_node_old_name`
2. `workflow_events`
   - insert compile-failed event

### Lifecycle visibility write

1. `node_versions`
   - update `status = COMPILE_FAILED`

### Writes that must not happen on failure

- no `compiled_workflows` row
- no `compiled_workflow_sources` rows for a successful workflow snapshot
- no `compiled_tasks`
- no `compiled_subtasks`
- no `node_runs`

## CLI results after failure

### Compile failure inspection

```yaml
node_version_id: proj_plan_v1
compile_failures:
  - failure_stage: override_resolution
    failure_class: override_missing_target
    target_family: task_definition
    target_id: review_node_old_name
```

### Run admission rejection

```json
{
  "status": "FAIL",
  "reason": "node_not_runnable",
  "summary": "Node proj_plan_v1 cannot start because no successful compiled workflow exists."
}
```

## Reattempt after override fix

### New YAML reads

Daemon rereads:

1. `.ai/overrides/tasks/review_node.yaml` after fix
2. all source files that participate in compile hash

### Successful relation checks

1. override target now resolves to existing `task_definition/review_node`
2. merged YAML validates
3. hooks and policy resolution succeed
4. compiled graph validation succeeds

## Durable DB writes on successful reattempt

1. `source_documents`
   - insert new row if changed override content has a new hash
2. `compiled_workflows`
   - insert `cw_proj_plan_v1`
3. `compiled_workflow_sources`
   - insert one row per source document used by `cw_proj_plan_v1`
4. `compiled_tasks`
5. `compiled_subtasks`
6. `compiled_subtask_dependencies`
7. `compiled_subtask_checks`
8. `workflow_events`
   - insert compile-succeeded event
9. lifecycle visibility write:
   - `node_versions.status = READY`

## Result

This simulation closes the failure-visibility hole:

- compile failure is durable
- run admission is rejected
- later recompile succeeds without erasing failure history

## Hole still visible

The compile and lifecycle docs are now aligned, but compile-attempt event naming still needs one bounded vocabulary across runtime, CLI, and simulations.
