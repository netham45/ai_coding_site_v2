# Flow B: Admit And Run A Ready Node

Sources:

- `notes/runtime_pseudocode_plan.md`
- `notes/runtime_command_loop_spec_v2.md`
- `notes/node_lifecycle_spec_v2.md`
- `notes/authority_and_api_model.md`

## Scenario

`plan_v1` exists, compiled successfully, and is `READY`.

## External action

```text
ai-tool node run start --node plan_v1
```

## Full task flow

### Step 1: daemon performs admission checks

Checks:

- compiled workflow exists
- node is not superseded
- node is not blocked by pause state
- dependencies are satisfied
- no incompatible active run exists

### Step 2: daemon creates run state

Durable writes:

```yaml
node_runs:
  id: run_plan_v1_1
  node_version_id: plan_v1
  run_status: RUNNING

node_run_state:
  node_run_id: run_plan_v1_1
  lifecycle_state: RUNNING
  current_task_id: research_context
  current_compiled_subtask_id: cst_plan_001
  current_subtask_attempt: 1
  is_resumable: true
```

### Step 3: daemon binds primary session

- creates or binds one primary session
- records tmux and provider identity if available
- marks session as authoritative execution agent for the run

### Step 4: daemon exposes current work

The session can now query:

- `subtask current`
- `subtask prompt`
- `subtask context`
- prior summaries
- dependency summaries

### Step 5: canonical node loop begins

The daemon does not yet advance the cursor.
It waits for the attempt lifecycle of the current compiled subtask.

## Simulated result

```json
{
  "status": "OK",
  "run_id": "run_plan_v1_1",
  "session_id": "sess_plan_v1_1",
  "lifecycle_state": "RUNNING",
  "current_task_id": "research_context",
  "current_compiled_subtask_id": "cst_plan_001"
}
```

## Logic issues exposed

1. The notes still do not fully freeze whether `node run start` always creates a new run or may bind to an already-active resumable run.
2. Admission ownership is clearly daemon-side in `authority_and_api_model.md`, but the CLI docs still present these as direct commands without much of the daemon decision surface visible.

