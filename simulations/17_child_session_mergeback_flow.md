# Child Session Merge-Back Flow

Source:

- `notes/child_session_mergeback_contract.md`

## Scenario

The parent pushes a bounded research child session.

## Full task flow

1. parent pushes child session
2. child performs bounded work
3. child emits structured return artifact
4. runtime validates artifact
5. runtime persists child result
6. runtime attaches result to parent context
7. parent resumes at same compiled subtask

Simulated return artifact:

```yaml
child_session_result:
  child_session_id: child_sess_1
  parent_node_id: plan_v1
  parent_compiled_subtask_id: cst_plan_003
  status: success
  summary: Repository is a small Python project.
  findings:
    - src/app.py is the likely implementation file
```

## Logic issues exposed

1. The DB model now makes `child_session_results` canonical, but dedicated CLI result-inspection surfaces for those records are still not fully frozen.
