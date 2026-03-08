# Child Session Round-Trip Flow

Sources:

- `notes/runtime_command_loop_spec_v2.md`
- `notes/child_session_mergeback_contract.md`
- `notes/database_schema_spec_v2.md`
- `notes/cli_surface_spec_v2.md`

## Scenario

Parent node `plan_v1` is in `research_context` subtask `plan_cst_001`.
It pushes a bounded child session to inspect the repository and returns structured findings to the same parent subtask.

## Starting state

### Required reads

1. `node_runs` for `run_plan_v1_1`
2. `node_run_state` for current cursor
3. `compiled_subtasks` for `plan_cst_001`
4. existing active primary session row in `sessions`

### Starting row shape

```yaml
node_run_state:
  node_run_id: run_plan_v1_1
  lifecycle_state: RUNNING
  current_task_id: task_research_context
  current_compiled_subtask_id: plan_cst_001
  current_subtask_attempt: 1
```

## CLI sequence

### Parent bind and inspect context

```text
ai-tool session bind --node plan_v1
ai-tool workflow current --node plan_v1
ai-tool subtask current --node plan_v1
ai-tool subtask context --node plan_v1
```

### Push child session

```text
ai-tool session push --node plan_v1 --reason research_context
```

### Child session work

Assumed child-session-local commands:

```text
rg --files .
```

### Pop with structured result

```text
ai-tool session pop --session child_sess_1 --summary-file .ai/summaries/child_sess_1.yaml
```

### Parent resumes same subtask and records summary

```text
ai-tool summary register --node plan_v1 --file .ai/summaries/plan_research.md --type subtask
ai-tool subtask current --node plan_v1
```

## Child result artifact read

`.ai/summaries/child_sess_1.yaml`

```yaml
child_session_result:
  child_session_id: child_sess_1
  parent_node_id: plan_v1
  parent_compiled_subtask_id: plan_cst_001
  status: success
  summary: Repository is a small Python project with one likely implementation path.
  findings:
    - src/app.py is the likely implementation file
    - tests/test_app.py is the likely focused test file
  artifacts: []
  suggested_next_actions:
    - create one child task
```

## Validation and relation checks

When `session pop` runs, daemon verifies:

1. `child_sess_1` exists in `sessions`
2. `child_sess_1.session_role = pushed_child`
3. `child_sess_1.parent_session_id` points to active primary parent session
4. result artifact child session ID matches CLI session ID
5. `parent_compiled_subtask_id = plan_cst_001`
6. `plan_cst_001` is still the parent’s current compiled subtask
7. artifact shape is valid
8. any declared artifact paths exist if listed

If any validation fails:

- result is not silently attached
- failure is recorded
- parent does not auto-advance

## Durable DB writes

### Parent push

1. `sessions`
   - insert child session row:
     - `id = child_sess_1`
     - `node_version_id = plan_v1`
     - `node_run_id = run_plan_v1_1`
     - `session_role = pushed_child`
     - `parent_session_id = sess_plan_v1_1`
     - `status = STARTING`
2. `session_events`
   - insert `bound`
   - insert `attached`
3. `workflow_events`
   - insert `child_session_pushed`

### Child becomes active

1. `sessions`
   - update `status = ACTIVE`
   - update `last_heartbeat_at`
2. `session_events`
   - insert `heartbeat` events while active

### Pop and merge-back

1. `child_session_results`
   - insert:
     - `child_session_id = child_sess_1`
     - `parent_compiled_subtask_id = plan_cst_001`
     - `status = success`
     - `result_json = child_session_result payload`
2. `session_events`
   - insert `completed`
3. `sessions`
   - update:
     - `status = COMPLETED`
     - `ended_at = now()`
4. `workflow_events`
   - insert `child_session_result_attached`
5. optional if attached summary is also mirrored:
   - `summaries`
     - insert `summary_type = subtask`
     - content references returned child result

### Parent summary write after evaluating child result

1. `summaries`
   - insert `plan_research.md` content
2. `subtask_attempts`
   - update or insert output snapshot for `plan_cst_001`

## Writes that must not happen

While the pushed child session is running:

- no parent cursor advancement in `node_run_state`
- no direct parent lifecycle mutation caused only by child session completion
- no child-session ownership of branch or git cursor

## Cursor invariants

### Before push

```yaml
current_compiled_subtask_id: plan_cst_001
```

### During child session

```yaml
current_compiled_subtask_id: plan_cst_001
```

### After pop

```yaml
current_compiled_subtask_id: plan_cst_001
```

Only after the parent runtime accepts the returned result and completes its own logic may the parent advance to the next subtask.

## Result

This simulation closes the earlier ambiguity:

- child session is a bounded helper
- its result is structured and validated
- merge-back is explicit
- the parent remains on the same compiled subtask until it decides otherwise

## Hole still visible

The notes now make `child_session_results` canonical in the DB spec, but CLI output examples for inspecting those results are still not separately frozen.
