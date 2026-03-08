# Resume After Interruption Flow

Sources:

- `notes/node_lifecycle_spec_v2.md`
- `notes/runtime_command_loop_spec_v2.md`
- `notes/session_recovery_appendix.md`
- `notes/database_schema_spec_v2.md`
- `notes/cli_surface_spec_v2.md`

## Scenario

`task_v1` is interrupted mid-subtask. The primary session becomes stale and tmux is lost. The daemon must recover from durable state and resume the same compiled subtask with a replacement session.

## Starting state

### Required rows

1. `node_runs`
   - `run_task_v1_1`
2. `node_run_state`
   - current cursor at `task_cst_004`
3. `subtask_attempts`
   - attempt 1 for `task_cst_004` exists and is in progress
4. `sessions`
   - `sess_task_v1_1` active primary session
5. `session_events`
   - prior `bound`, `heartbeat`

### Starting snapshot

```yaml
node_run_state:
  node_run_id: run_task_v1_1
  lifecycle_state: RUNNING
  current_task_id: execute_node
  current_compiled_subtask_id: task_cst_004
  current_subtask_attempt: 1
  last_completed_compiled_subtask_id: task_cst_003
  is_resumable: true
  working_tree_state: dirty_expected
```

## Interruption

Observed runtime facts:

- heartbeat stops for `sess_task_v1_1`
- tmux session is missing
- process-level continuity is gone
- durable run state still says subtask `task_cst_004` is current

## CLI sequence

### Operator or daemon inspects current state

```text
ai-tool node run show --node task_v1
ai-tool subtask current --node task_v1
ai-tool subtask attempts --node task_v1
ai-tool node events --node task_v1
```

### Recovery-triggered inspection

Assumed daemon-internal equivalent or future operator command:

```text
ai-tool session show --node task_v1
ai-tool session events --node task_v1
```

### Resume path

```text
ai-tool node resume --node task_v1
ai-tool node run show --node task_v1
```

## Recovery reads

Daemon reads:

1. `node_runs` for latest active run
2. `node_run_state` for cursor truth
3. `sessions` for current primary session record
4. `session_events` for last heartbeat / detach / failure clues
5. `subtask_attempts` for current in-progress attempt
6. `compiled_workflows`
7. `compiled_subtasks` for `task_cst_004`
8. current git branch/head from runtime environment

## Recovery relation checks

1. run exists and `run_status = RUNNING`
2. `node_run_state.is_resumable = true`
3. current compiled subtask belongs to run’s compiled workflow
4. session `sess_task_v1_1` is no longer healthy enough to reuse
5. no other active primary session already owns the run
6. git branch/head are compatible with expected node branch
7. if git branch/head are incompatible, recovery must not guess

## Durable DB writes during recovery

### Mark original session stale or failed

1. `sessions`
   - update `sess_task_v1_1.status = STALE` or `FAILED`
   - update `ended_at` if terminal
2. `session_events`
   - insert `failed` or `invalidated`

### Record recovery attempt

1. `workflow_events`
   - insert `recovery_attempted`

### Create replacement session

1. `sessions`
   - insert `sess_task_v1_2`:
     - `node_version_id = task_v1`
     - `node_run_id = run_task_v1_1`
     - `session_role = primary`
     - `status = STARTING`
2. `session_events`
   - insert `replacement_created`
   - insert `bound`
3. `workflow_events`
   - insert `replacement_session_created`

### Rebind and resume

1. `sessions`
   - update `sess_task_v1_2.status = ACTIVE`
2. `session_events`
   - insert `resumed`
3. `workflow_events`
   - insert `recovery_succeeded`

### Writes that must not happen

- no advancement of `current_compiled_subtask_id`
- no new `node_runs` row
- no overwrite of prior `subtask_attempts` history

## Resume context reconstructed

The daemon reconstructs prompt/context for the replacement session from:

1. compiled subtask definition
2. prior successful subtask outputs
3. current subtask attempt record
4. current working-tree and git-head knowledge

## Replacement-session prompt boundary

Assumed reissue payload:

```yaml
resume_context:
  node_version_id: task_v1
  node_run_id: run_task_v1_1
  compiled_workflow_id: cw_task_v1
  current_compiled_subtask_id: task_cst_004
  current_subtask_attempt: 1
  last_completed_compiled_subtask_id: task_cst_003
  recovery_mode: replacement_session
```

## Completion after resume

If resumed work succeeds:

1. `subtask_attempts`
   - update current attempt to `SUCCEEDED`
2. `node_run_state`
   - advance `last_completed_compiled_subtask_id`
   - advance `current_compiled_subtask_id` to next subtask
3. `workflow_events`
   - insert normal cursor-advanced event

If recovery discovers git mismatch:

1. `node_run_state`
   - update `lifecycle_state = PAUSED_FOR_USER` or another failure path per policy
2. `workflow_events`
   - insert `recovery_failed_git_mismatch`
3. `summaries`
   - insert operator-visible summary

## Result

This simulation shows the key recovery guarantee:

- durable run state is authoritative
- the system resumes the same compiled subtask
- replacement session creation is explicit and inspectable

## Hole still visible

The docs distinguish many recovery scenarios, but the simulation set still needs the complementary “healthy detached session reused successfully” path.
