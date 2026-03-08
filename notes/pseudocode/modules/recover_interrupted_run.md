# Module: `recover_interrupted_run(...)`

## Purpose

Recover an interrupted node run by reusing a valid existing session when safe, or creating a replacement session when necessary, while preserving the authoritative cursor and preventing duplicate session ownership.

---

## Source notes

Primary:

- `notes/session_recovery_appendix.md`
- `notes/runtime_command_loop_spec_v2.md`

Supporting:

- `notes/node_lifecycle_spec_v2.md`
- `notes/cli_surface_spec_v2.md`
- `notes/cutover_policy_note.md`
- `notes/authority_and_api_model.md`

---

## Inputs

- `node_id` or `run_id`
- active run state
- active primary session record if any
- latest subtask attempt state
- tmux existence check result if available
- provider session identity if available
- git branch/head state

---

## Required state

- durable run state is considered authoritative unless explicitly proven stale
- current compiled workflow binding is durable
- current compiled subtask ID and attempt history are durable
- resumability flag is durable and queryable

---

## Outputs

- `RecoveryResult(status = "reused_existing_session" | "replacement_session_created" | "recovery_rejected" | "paused_for_user")`

Optional outputs:

- authoritative session ID
- replacement session ID
- recovery summary
- mismatch diagnostics

---

## Durable writes

- recovery-attempt event
- session validity classification
- replacement-session creation and binding where applicable
- duplicate-session invalidation where applicable
- pause or mismatch event where applicable

---

## Decision algorithm

```text
function recover_interrupted_run(node_id):
  run = load_active_run_for_node(node_id)
  if run is null:
    return RecoveryResult(status = "recovery_rejected", reason = "no_active_run")

  state = load_authoritative_run_state(run.id)
  record_recovery_attempt(run.id)

  if state.is_resumable is false:
    record_recovery_rejected(run.id, "non_resumable_run")
    return RecoveryResult(status = "recovery_rejected", reason = "non_resumable_run")

  session = load_active_primary_session(run.id)
  git_state = inspect_git_state_for_run(run.id)
  assert compiled_workflow_exists(run.compiled_workflow_id)

  if git_state_mismatches_authoritative_cursor(git_state, state):
    record_git_mismatch_event(run.id, git_state, state)
    transition_run_to_paused(run.id, pause_flag_name = "git_state_mismatch")
    return RecoveryResult(status = "paused_for_user")

  duplicate_sessions = find_duplicate_active_primary_sessions(run.id)
  if duplicate_sessions_exist(duplicate_sessions):
    invalidate_or_mark_ambiguous_duplicate_sessions(run.id, duplicate_sessions)
    transition_run_to_paused(run.id, pause_flag_name = "duplicate_primary_session")
    return RecoveryResult(status = "paused_for_user")

  session_class = classify_existing_session(session, state)

  if session_class in ["healthy", "detached"]:
    refresh_or_rebind_existing_session(run.id, session.id)
    reload_current_cursor_context(run.id)
    record_recovery_success(run.id, "reused_existing_session", session.id)
    return RecoveryResult(status = "reused_existing_session", session_id = session.id)

  if session_class == "stale_but_recoverable":
    nudge_idle_session(run.id, session.id)
    if session_recovers_after_nudge(session.id):
      refresh_or_rebind_existing_session(run.id, session.id)
      reload_current_cursor_context(run.id)
      record_recovery_success(run.id, "reused_existing_session", session.id)
      return RecoveryResult(status = "reused_existing_session", session_id = session.id)

  if session_class in ["lost", "missing"]:
    replacement = create_replacement_primary_session(run.id, state.current_compiled_subtask_id)
    bind_replacement_session_to_run(run.id, replacement.id)
    reload_current_cursor_context(run.id)
    record_recovery_success(run.id, "replacement_session_created", replacement.id)
    return RecoveryResult(status = "replacement_session_created", session_id = replacement.id)

  transition_run_to_paused(run.id, pause_flag_name = "ambiguous_recovery_state")
  return RecoveryResult(status = "paused_for_user")
```

---

## Session classification

The session classifier should distinguish at least:

- `healthy`
- `detached`
- `stale_but_recoverable`
- `lost`
- `missing`
- `ambiguous`

Inputs should include heartbeat freshness, tmux existence, provider resume possibility, and uniqueness of ownership.

---

## Recovery rules

- prefer reuse when a single valid authoritative session exists
- do not create a replacement session if ownership is ambiguous
- if provider session recovery is unavailable, recovery must still work from durable run state plus tmux/git inspection when possible
- replacement sessions resume from durable cursor state, not inferred human memory

---

## Failure paths

### Non-resumable run

- reject automatic recovery
- preserve the reason

### Git state mismatch

- do not blindly resume
- pause for user or controlled rectification path

### Duplicate active primary sessions

- treat as invariant violation
- stop automatic execution until ownership is clear

### Missing compiled workflow

- reject recovery
- require operator intervention or explicit rectification

---

## CLI-visible expectations

Operators should be able to inspect:

- last recovery attempt
- authoritative active session
- whether a replacement session was created
- why recovery was rejected or paused

---

## Open questions

- when provider-specific resume should be attempted before replacement versus treated as an optional later optimization
- whether some git mismatches should trigger automatic safe reset rather than immediate pause

---

## Pseudotests

### `reuses_detached_but_healthy_session`

Given:

- heartbeat/session state indicates the primary session is still valid

Expect:

- no replacement session is created
- the run resumes from the existing session

### `creates_replacement_when_original_session_is_lost`

Given:

- run is resumable
- tmux session is gone
- no ownership ambiguity exists

Expect:

- replacement session is created and bound
- cursor context is reloaded from durable state

### `pauses_on_duplicate_primary_session_invariant_violation`

Given:

- more than one active primary session appears for the run

Expect:

- execution is paused
- no new replacement session is created automatically
