# Flow A: Create And Compile A New Top-Level Node

Sources:

- `notes/runtime_pseudocode_plan.md`
- `notes/yaml_schemas_spec_v2.md`
- `notes/override_conflict_semantics.md`
- `notes/hook_expansion_algorithm.md`
- `notes/compile_failure_persistence.md`
- `notes/authority_and_api_model.md`

## Scenario

The operator creates a top-level `plan` node from a request file.

## Input request

```yaml
request:
  title: Greeting starter
  prompt: >
    Create a greeting generator that reads greetings.yaml and writes
    greeting.txt.
  target_kind: plan
```

## External action

```text
ai-tool node create --kind plan --title "Greeting starter" --file .ai/requests/greeting.yaml
```

## Full task flow

### Step 1: daemon accepts mutation

- CLI calls daemon
- daemon allocates `logical_node_id`
- daemon creates `node_versions` row in `DRAFT`

Simulated durable state:

```yaml
node_versions:
  id: plan_v1
  logical_node_id: plan_logical_1
  node_kind: plan
  status: DRAFT
```

### Step 2: source discovery

Compiler discovers:

- built-in `node_definition` for `plan`
- built-in task definitions named in `available_tasks`
- subtask definitions, review/testing/docs refs
- project-local policy docs
- project-local extensions
- project-local overrides

### Step 3: source loading

Each discovered doc becomes a `source_documents` row.

### Step 4: extension resolution

Project-local extensions are loaded before overrides.

### Step 5: override resolution

The compiler applies merge modes by family and field.

Important checks:

- target family exists
- target document exists
- merge mode is valid for the targeted field
- no ambiguous duplicate bases exist

### Step 6: schema validation

The compiler validates:

- node definition
- task definitions
- subtask definitions
- override definitions
- review/testing/docs definitions

### Step 7: policy resolution

Project policy is folded into the compile context.

Example:

```yaml
resolved_policy:
  auto_run_children: true
  require_review_before_finalize: true
  require_testing_before_finalize: true
  require_docs_before_finalize: true
```

### Step 8: hook expansion

The compiler:

1. collects candidate hooks
2. filters by insertion point and applicability
3. orders them deterministically
4. expands them into explicit compiled stages
5. validates that the resulting workflow is still structurally legal

### Step 9: workflow compilation

The compiler emits:

- `compiled_workflows`
- `compiled_tasks`
- `compiled_subtasks`
- `compiled_subtask_checks`
- `compiled_subtask_dependencies`
- `compiled_workflow_sources`

Simulated compiled task order:

1. `research_context`
2. `generate_child_layout`
3. `review_child_layout`
4. `spawn_children`
5. `wait_for_children`
6. `reconcile_children`
7. `validate_node`
8. `review_node`
9. `test_node`
10. `update_provenance`
11. `build_node_docs`
12. `finalize_node`

### Step 10: compiled graph validation

The compiler checks:

- no invalid compiled subtask graph
- no bad hook insertions
- no invalid task ordering
- no dependency graph corruption

### Step 11: persistence and READY transition

The workflow is persisted and the node becomes `READY`.

## Simulated result

```json
{
  "status": "OK",
  "node_version_id": "plan_v1",
  "compiled_workflow_id": "cw_plan_v1",
  "lifecycle_state": "READY"
}
```

## Logic issues exposed

1. The daemon/API authority model is clearer than the CLI docs; the CLI wording still under-specifies daemon-side validation and locking behavior.
2. Hook expansion can materially change the workflow, but the exact equivalence rule for “duplicate semantic stages” is still not frozen.
