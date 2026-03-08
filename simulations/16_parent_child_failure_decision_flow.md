# Parent Child Failure Decision Flow

Source:

- `notes/parent_failure_decision_spec.md`

## Scenario

`task_b_v1` fails during `test_node`.

## Full task flow

### Step 1: record failure impact

Initial counters:

```yaml
total_child_failures: 0
consecutive_child_failures: 0
per_child_failures:
  task_b_v1: 0
```

After recording:

```yaml
total_child_failures: 1
consecutive_child_failures: 1
per_child_failures:
  task_b_v1: 1
```

### Step 2: classify failure

```yaml
failure_class: test_failure
```

### Step 3: threshold check

Thresholds are not exceeded.

### Step 4: retry suitability

Because test failures may be retryable and retry budget remains, parent chooses retry.

### Step 5: persist parent decision

```yaml
event_type: parent_retry_child
payload:
  failed_child_id: task_b_v1
  failure_class: test_failure
```

## Logic issues exposed

1. The algorithm is clear, but the default built-in flow inventory still does not clearly show where `respond_to_child_failure` is inserted relative to `wait_for_children`.

