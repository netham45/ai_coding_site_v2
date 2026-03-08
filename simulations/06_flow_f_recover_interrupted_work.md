# Flow F: Recover Interrupted Work

Sources:

- `notes/runtime_pseudocode_plan.md`
- `notes/session_recovery_appendix.md`
- `notes/runtime_command_loop_spec_v2.md`

## Scenario

`run_task_v1_1` is mid-subtask. The tmux session disappeared, but durable run state is intact.

## Full task flow

### Step 1: operator requests recovery

```text
ai-tool session resume --node task_v1
```

### Step 2: daemon loads authoritative run state

It inspects:

- active run
- current subtask
- attempt number
- active session record
- tmux session existence
- git head safety
- `is_resumable`

Simulated classification:

```yaml
run_state: resumable
primary_session: lost
tmux_session: missing
cursor_state: intact
git_state: safe
```

### Step 3: daemon chooses recovery path

Because:

- run is resumable
- no valid current session remains
- git/cursor are safe

the daemon creates a replacement session.

### Step 4: replacement session is bound

```json
{
  "status": "OK",
  "recovery_action": "replacement_session_created",
  "old_session_id": "sess_task_v1_1",
  "new_session_id": "sess_task_v1_2",
  "resumed_subtask_id": "cst_task_022"
}
```

### Step 5: same cursor resumes

The daemon restores:

- same compiled workflow
- same compiled subtask
- same logical execution position

It does not auto-advance the cursor.

## Logic issues exposed

1. The recovery appendix is good on scenarios, but the canonical specs still do not fully define which recovery outcomes must become workflow events versus session events.
2. Old-session invalidation semantics after replacement are still only partly explicit.

