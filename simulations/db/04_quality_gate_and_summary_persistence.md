# DB Simulation: Quality Gates And Summary Persistence

Sources:

- `notes/database_schema_spec_v2.md`
- `notes/review_testing_docs_yaml_plan.md`
- `notes/state_value_catalog.md`

## Scenario

A child task completes validation, review, testing, docs, and summary generation.

## Simulated durable operations

### Step 1: validation rows

```yaml
inserts:
  - table: validation_results
    values:
      id: vr_001
      node_version_id: task_v1
      node_run_id: run_task_v1_1
      compiled_subtask_id: cst_validate_01
      check_type: file_exists
      status: PASS
      summary: greetings.yaml exists
  - table: validation_results
    values:
      id: vr_002
      node_version_id: task_v1
      node_run_id: run_task_v1_1
      compiled_subtask_id: cst_validate_02
      check_type: command_exit_code
      status: PASS
      summary: pytest exited 0
```

### Step 2: review row

```yaml
insert:
  table: review_results
  values:
    id: rr_001
    node_version_id: task_v1
    node_run_id: run_task_v1_1
    compiled_subtask_id: cst_review_01
    review_definition_id: node_against_requirements
    scope: node_output
    status: PASS
    findings_json: "[]"
    summary: Implementation aligned with requirements
```

### Step 3: test row

```yaml
insert:
  table: test_results
  values:
    id: tr_001
    node_version_id: task_v1
    node_run_id: run_task_v1_1
    compiled_subtask_id: cst_test_01
    testing_definition_id: default_unit_test_gate
    suite_name: pytest
    status: PASS
    attempt_number: 1
    summary: 1 passed
```

### Step 4: summary row

```yaml
insert:
  table: summaries
  values:
    id: sum_001
    node_version_id: task_v1
    node_run_id: run_task_v1_1
    summary_type: subtask
    content: Greeting task completed successfully
```

### Step 5: docs row

```yaml
insert:
  table: node_docs
  values:
    id: doc_001
    node_version_id: task_v1
    view_scope: local
    doc_kind: node_summary
    path: .ai/docs/task_v1/local.md
    content_hash: doc_hash_001
```

## Logic issues exposed

1. The DB spec has dedicated result tables, but it still leaves some result taxonomies open-ended as `text`.
2. There is still no canonical provenance result table in the same way quality-gate results are modeled.

