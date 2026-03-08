# DB Simulation: Top-Level Node Creation

Sources:

- `notes/database_schema_spec_v2.md`
- `notes/database_schema_v2_expansion.md`
- `notes/yaml_schemas_spec_v2.md`
- `notes/compile_failure_persistence.md`

## Scenario

Create a top-level `plan` node from a request file and compile it successfully.

## Simulated durable operations

### Step 1: insert `node_versions`

```yaml
insert:
  table: node_versions
  values:
    id: plan_v1
    logical_node_id: plan_logical_1
    parent_node_version_id: null
    tier: plan
    node_kind: plan
    title: Greeting starter
    description: Create a greeting generator
    status: DRAFT
    version_number: 1
    supersedes_node_version_id: null
    active_branch_name: tier/plan/plan/greeting-starter__plan_v1
    branch_generation_number: 1
```

### Step 2: insert discovered `source_documents`

Examples:

```yaml
inserts:
  - table: source_documents
    values:
      id: src_001
      doc_family: node_definition
      path: builtins/nodes/plan.yaml
      source_scope: built_in
      content_hash: hash_plan_builtin
      merge_mode: replace
  - table: source_documents
    values:
      id: src_002
      doc_family: task_definition
      path: builtins/tasks/research_context.yaml
      source_scope: built_in
      content_hash: hash_task_research
      merge_mode: replace
```

### Step 3: insert `compiled_workflows`

```yaml
insert:
  table: compiled_workflows
  values:
    id: cw_plan_v1
    node_version_id: plan_v1
    source_hash: source_hash_123
    resolved_yaml: "{...}"
```

### Step 4: insert `compiled_workflow_sources`

```yaml
inserts:
  - compiled_workflow_id: cw_plan_v1
    source_document_id: src_001
    source_role: base_node_definition
  - compiled_workflow_id: cw_plan_v1
    source_document_id: src_002
    source_role: task_definition
```

### Step 5: insert `compiled_tasks`

Example rows:

```yaml
inserts:
  - id: ct_001
    compiled_workflow_id: cw_plan_v1
    task_key: research_context
    ordinal: 1
  - id: ct_002
    compiled_workflow_id: cw_plan_v1
    task_key: generate_child_layout
    ordinal: 2
```

### Step 6: insert `compiled_subtasks`

Example rows:

```yaml
inserts:
  - id: cst_001
    compiled_workflow_id: cw_plan_v1
    compiled_task_id: ct_001
    source_subtask_key: build_context
    ordinal: 1
    subtask_type: build_context
  - id: cst_002
    compiled_workflow_id: cw_plan_v1
    compiled_task_id: ct_001
    source_subtask_key: spawn_child_session
    ordinal: 2
    subtask_type: spawn_child_session
```

### Step 7: update node to `READY`

```yaml
update:
  table: node_versions
  where:
    id: plan_v1
  set:
    status: READY
    updated_at: now()
```

### Step 8: insert current-version selector row

```yaml
insert:
  table: logical_node_current_versions
  values:
    logical_node_id: plan_logical_1
    authoritative_node_version_id: plan_v1
    latest_created_node_version_id: plan_v1
```

## Logic issues exposed

1. `node_versions.status` is doing a lot of work while `node_run_state.lifecycle_state` also carries lifecycle semantics. The split is directionally good, but easy to misuse.
2. Compile success has a clear durable story; compile failure does too. The intermediate `COMPILED` state still feels underused relative to `READY`.
