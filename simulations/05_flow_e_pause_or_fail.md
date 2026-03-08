# Flow E: Pause Or Fail

Sources:

- `notes/runtime_pseudocode_plan.md`
- `notes/node_lifecycle_spec_v2.md`
- `notes/review_testing_docs_yaml_plan.md`
- `notes/pause_workflow_event_persistence.md`

## Scenario

A review stage returns `REVISE`, then a later retry still does not satisfy policy, so the node pauses for the user.

## Full task flow

### Step 1: review returns a non-pass result

```json
{
  "status": "REVISE",
  "summary": "Acceptance criteria are still undersatisfied. Summary artifact missing."
}
```

### Step 2: runtime applies built-in or policy-defined revise behavior

Possible options from the notes:

- rerun subtask
- rerun task
- pause for user

Assume local policy allows one retry.

### Step 3: retry path completes and review still does not pass

At this point the runtime:

- records failure/revise summary
- sets pause flag
- transitions to `PAUSED_FOR_USER`

### Step 4: persist pause event

```yaml
event_type: pause_entered
event_scope: pause
payload:
  pause_flag: review_revision_required
  triggering_stage: review_node
```

### Step 5: expose pause state

```text
ai-tool node pause-state --node task_v1
```

Simulated result:

```yaml
lifecycle_state: PAUSED_FOR_USER
pause_flag_name: review_revision_required
summary_type: pause
```

## Logic issues exposed

1. The default behavior for `REVISE` is still not canonically frozen for the built-in library.
2. The boundary between `session_events` and canonical `workflow_events` still needs disciplined implementation guidance.
