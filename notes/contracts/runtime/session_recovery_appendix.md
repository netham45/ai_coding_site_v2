# Session Recovery Appendix

## Purpose

This document defines the recovery model for interrupted node runs and their sessions.

The system already assumes:

- one active run per node version
- one primary session per active run
- tmux-backed sessions
- provider session identity when available
- durable run and cursor state in the database

What remained underspecified was the edge-case behavior when those pieces disagree or disappear.

This appendix makes the recovery model explicit enough to support:

- runtime implementation
- CLI semantics
- auditability review
- no-hidden-state guarantees

Related documents:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`

---

## Core Recovery Rule

Recovery should be driven first by durable orchestration state, not by fragile external session state.

Recovery priority order:

1. preserve correct cursor state
2. avoid duplicate active primary sessions
3. reuse an existing valid session when safely possible
4. create a replacement session when reuse is unsafe or impossible

If provider or tmux state conflicts with durable node-run state, the database-backed run state is authoritative unless the system explicitly proves it is stale.

Current primary-session identity should be resolved from canonical session state rather than a duplicated run-level session pointer.

---

## Recovery Inputs

The recovery decision should inspect at least:

- node version ID
- active node run ID
- node lifecycle state
- current run lifecycle state
- current compiled subtask ID
- current subtask attempt number
- last completed compiled subtask ID
- active primary session record
- session role/status/heartbeat
- tmux session existence if checkable
- provider session ID if available
- current branch and git head
- is_resumable flag

---

## Recovery Scenarios

The runtime should distinguish at least the following cases.

## Case 1: Session healthy and attached

Condition:

- active session exists
- recent heartbeat exists
- tmux session exists or session can still be attached

Action:

- do not create a replacement session
- simply reattach or resume through the current session path

## Case 2: Session healthy but detached

Condition:

- active session exists
- recent heartbeat or good status exists
- user/operator is no longer attached

Action:

- reattach to the existing session
- do not create a replacement session

Implementation staging note:

- the current implementation records this as an `attached` session event on the durable primary session row

## Case 3: Session stale but tmux session still exists

Condition:

- active session record exists
- heartbeat is stale
- tmux session still exists

Action:

- inspect whether the session is genuinely stuck or only quiet
- optionally nudge first
- if session responds, resume existing session
- if session remains stuck, mark recovery event and consider replacement

## Case 4: Session record exists but tmux session is gone

Condition:

- active session record exists
- tmux session no longer exists

Action:

- treat the original session as lost
- create replacement session if run is resumable
- preserve old session history

Implementation staging note:

- the current implementation now marks the old durable session row `LOST`, records an invalidation event, and creates a replacement primary session row bound to the same active run
- replacement and fresh primary sessions now use concrete tmux launch plans derived from durable run/session identity and persist the launch metadata into session events for auditability

## Case 5: Provider session exists but tmux is lost

Condition:

- provider session ID exists or appears resumable
- tmux session is gone

Action:

- if provider resume can be rebound safely, attempt rebinding
- if not, create replacement session using durable run state

Rule:

- provider-specific recovery is optional enhancement, not the primary recovery foundation

## Case 6: Run resumable but no viable session remains

Condition:

- active run exists
- no valid primary session can be recovered
- cursor state is intact

Action:

- create a replacement primary session
- bind it to the active run
- resume from the current compiled subtask

## Case 7: Run marked non-resumable

Condition:

- `is_resumable = false`

Action:

- do not auto-resume
- pause for user or require explicit operator intervention

## Case 8: Git state mismatch

Condition:

- durable run state points to one subtask/cursor
- actual branch/head state does not match expected execution position

Action:

- do not blindly resume
- record mismatch
- either:
  - reconcile back to known safe state
  - pause for user
  - initiate controlled rectification if policy allows

## Case 9: Multiple active primary sessions appear

Condition:

- duplicate primary sessions are detected for one active run

Action:

- treat as invariant violation
- choose one session as authoritative only after inspection
- mark extras as invalidated or superseded
- pause automatic execution if ownership is ambiguous

---

## Session Recovery Decision Order

The recommended default recovery order is:

## Step 1: Load authoritative run state

Load:

- active run
- run state
- active primary session
- latest subtask attempt
- lifecycle state

If no active run exists:

- recovery should not create one implicitly unless the user explicitly requested a new run

## Step 2: Check resumability

If the run is not resumable:

- stop automatic recovery
- expose the reason
- pause for user or operator action

## Step 3: Check active session validity

If the active primary session exists:

- inspect heartbeat freshness
- inspect tmux existence
- inspect provider resume possibility if available

Then classify the session as:

- `healthy`
- `detached`
- `stale_but_recoverable`
- `lost`
- `ambiguous`

If a replacement session is created:

- the old primary session should be marked invalidated in canonical session state
- recovery history should be visible through workflow and session event records
- the new primary session should expose enough tmux metadata to attach deterministically without guessing the session name out of band

## Step 4: Prefer reuse if safe

Reuse the session if:

- there is a single authoritative primary session
- tmux/provider state is compatible enough
- cursor ownership is unambiguous

## Step 5: Create replacement session if needed

Create replacement session if:

- the run is resumable
- the old session is lost or unusable
- no duplicate-active-session ambiguity exists
- git/cursor state is safe enough to continue

## Step 6: Reload current work

The recovered or replacement session must load:

- current compiled workflow
- current compiled subtask
- current prompt/command/context
- prior summaries and attempt history relevant to the current stage

## Step 7: Resume from cursor, not from guesswork

Resume must continue from the durable current subtask pointer.

The system must not:

- silently skip the current subtask
- silently replay already accepted subtasks
- assume terminal buffer history is required for correctness

---

## Replacement Session Rule

Replacement sessions are expected, normal recovery mechanisms.

When a replacement session is created:

1. preserve the prior session record
2. record a session event explaining replacement reason
3. bind the new session as the active primary session
4. keep the same active run if the run remains resumable
5. reissue current stage context through CLI

This should not require creating a new node run unless the existing run is no longer valid.

---

## Recovery Prompt Payloads

Recovery should use authored prompt payloads rather than ad hoc operator text.

The default versions live in `notes/specs/prompts/prompt_library_plan.md`.

## Resume existing session payload

```text
Resume active work for node <node_id>.

Recovered state:
- run id: <run_id>
- compiled subtask: <compiled_subtask_id>
- attempt number: <attempt_number>

Reload the current prompt and context through CLI before continuing:
- `ai-tool subtask current --node <node_id>`
- `ai-tool subtask prompt --node <node_id>`
- `ai-tool subtask context --node <node_id>`

Continue from the durable cursor. Do not skip or replay accepted subtasks.
```

## Replacement session payload

```text
You are a replacement session for node <node_id>.

Authoritative recovery state:
- run id: <run_id>
- compiled subtask: <compiled_subtask_id>
- attempt number: <attempt_number>
- recovery reason: <recovery_reason>

Before doing work:
1. inspect current work through CLI
2. confirm the current stage contract
3. send a heartbeat

Required CLI:
- `ai-tool subtask current --node <node_id>`
- `ai-tool subtask prompt --node <node_id>`
- `ai-tool subtask context --node <node_id>`
- `ai-tool subtask heartbeat --compiled-subtask <compiled_subtask_id>`

If local git or output state does not match the current stage, stop and fail
safely rather than guessing.
```

---

## Provider-Agnostic Recovery Rule

Provider session identity is useful but not required.

The system should be able to recover even if:

- provider session ID is absent
- provider resume is unsupported
- provider resume is unreliable

That is why the real recovery anchor is:

- compiled workflow
- durable cursor
- subtask attempt history
- summaries
- git state
- tmux or replacement-session orchestration

---

## Git State Safety Checks

Before resuming any recovered or replacement session, the runtime should verify:

- current branch matches expected node branch
- git head is compatible with the current run position
- working tree is not in an unexpected destructive/conflicted state

If these checks fail:

- record a recovery mismatch
- do not continue automatically unless policy allows safe correction
- prefer pause for user or controlled reconciliation

---

## Nudge Before Replace Policy

If a session is stale but not clearly lost, the default should usually be:

1. inspect state
2. nudge the session
3. wait bounded time
4. replace only if still unresponsive or invalid

This prevents unnecessary replacement churn.

Recommended exceptions:

- tmux session is gone
- duplicate-active-session ambiguity exists
- session is clearly in invalid state

---

## Pseudocode

```python
def recover_interrupted_run(node_id):
    run = load_active_run(node_id)
    if run is None:
        return "no_active_run"

    state = load_run_state(run.id)
    if not state.is_resumable:
        transition_run_to_paused(run.id, reason="not_resumable")
        return "paused_not_resumable"

    session = load_active_primary_session(run.id)
    classification = classify_session_health(session, run.id)

    if classification in ("healthy", "detached"):
        return resume_existing_session(session.id)

    if classification == "stale_but_recoverable":
        nudge_idle_session(run.node_version_id)
        classification = recheck_session_health(session.id)
        if classification in ("healthy", "detached"):
            return resume_existing_session(session.id)

    if classification == "ambiguous":
        transition_run_to_paused(run.id, reason="ambiguous_session_ownership")
        return "paused_ambiguous_session"

    if not git_state_matches_run(run.id):
        transition_run_to_paused(run.id, reason="git_state_mismatch")
        return "paused_git_mismatch"

    replacement = create_replacement_primary_session(run.id)
    bind_session_to_run(replacement.id, run.id)
    reissue_current_stage_context(run.id, replacement.id)
    return "replacement_session_created"
```

---

## DB Implications

The current v2 DB model supports much of this through:

- `node_runs`
- `node_run_state`
- `sessions`
- `session_events`
- `subtask_attempts`

Possible future additions if needed:

- a more explicit recovery-event table
- a recovery-classification field on session events

Likely good-enough first implementation:

- represent recovery decisions through `session_events`
- keep current-state authority in `node_run_state`

Implementation staging note:

- the current implementation now follows that staged model directly: recovery attempts, resumptions, replacements, pauses, and rejections are written to `session_events`
- no separate recovery-event table has been introduced yet because the current session and run-state schema is sufficient for provider-agnostic recovery classification

---

## CLI Implications

The following CLI capabilities are especially important for recovery:

- `ai-tool session show --node <id>`
- `ai-tool session events --session <id>`
- `ai-tool session resume --node <id>`
- `ai-tool session recover --node <id>`
- `ai-tool session attach --node <id>`
- `ai-tool session nudge --node <id>`
- `ai-tool node pause-state --node <id>`
- `ai-tool subtask current --node <id>`
- `ai-tool node recovery-status --node <id>`

If names differ, these capabilities should still exist.

---

## Interaction With Parent Failure Logic

If recovery fails repeatedly for a child node:

- that may become a child failure signal
- the parent should then decide whether to retry, regenerate, replan, or pause

This means session recovery failure should integrate with the broader failure-class system rather than being treated as a special uncategorized case.

---

## Auditability Requirements

Recovery should be auditable enough to answer:

- what run was recovered
- what session was reused or replaced
- why replacement occurred
- whether tmux, provider, or git mismatch caused the change
- what current subtask was resumed

If the system cannot answer those questions, recovery is too opaque.

---

## Recommended Next Follow-On Work

The next docs that should absorb this logic are:

1. `notes/specs/runtime/runtime_command_loop_spec_v2.md`
2. `notes/specs/database/database_schema_spec_v2.md`
3. `notes/specs/cli/cli_surface_spec_v2.md`
4. `notes/catalogs/traceability/cross_spec_gap_matrix.md`

Then reduce the severity of the session-recovery gap.

---

## Exit Criteria

This appendix is complete enough when:

- recovery scenarios are enumerated
- replacement-session behavior is explicit
- provider-agnostic recovery is explicit
- git mismatch behavior is explicit
- DB and CLI implications are identified

At that point, session recovery no longer depends on vague intuition.
