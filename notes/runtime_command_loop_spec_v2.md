# Runtime Command Loop Spec V2

## Purpose

This document defines the canonical AI-facing execution loop for nodes, compiled subtasks, tmux-backed sessions, pushed child sessions, and CLI-driven runtime control.

V2 expands the prior runtime loop spec by:

- aligning the loop with the v2 lifecycle model
- aligning the loop with explicit review/testing/docs result handling
- clarifying actor ownership between session, runtime, and durable state
- clarifying recovery and idle-session behavior
- clarifying child-node and pushed-child-session orchestration
- clarifying daemon/API authority boundaries

Design goals:

- the same CLI should serve both operators and AI sessions
- no critical runtime state should exist only in memory
- every node run should be resumable from durable state
- execution should always be explainable from compiled workflow plus durable history
- the daemon should be the live orchestration authority while durable state remains recoverable from the database

---

## 1. Core runtime model

### Primary rule

Default behavior:

- one node version
- one active node run
- one primary session binding
- one compiled workflow cursor

That means:

- the node run is the durable execution owner
- the primary session is the active execution agent
- the compiled workflow defines the executable stages
- the daemon is the live orchestration authority
- the database is the durable canonical record for runtime state and history

### Client access rule

Operational clients should talk to the daemon API rather than coordinating directly through database access.

Recommended initial access model:

- HTTPS transport
- runtime-generated cookie authentication
- CLI and future web/dashboard clients acting as daemon clients

### Optional pushed child session

A subtask may temporarily push work into a bounded child session when context isolation is useful.

Examples:

- research
- review
- focused verification
- summarization

This push/pop mechanism is for context management only.

It does not transfer:

- node ownership
- branch ownership
- compiled workflow ownership
- cursor ownership

The parent session remains the owner of node execution.

---

## 2. Actor ownership model

The runtime needs explicit ownership boundaries.

### Node run

Owns:

- compiled workflow binding
- current cursor state
- lifecycle state
- durable execution history

### Primary session

Owns:

- active interaction with the current subtask
- heartbeats
- prompt/context retrieval
- progress commands

### Pushed child session

Owns:

- bounded delegated context work
- delegated summary output

### Runtime/orchestrator layer

Owns:

- run admission
- session binding/rebinding
- idle detection
- recovery logic
- child scheduling
- upstream rebuild orchestration
- API request validation and mutation authorization
- persistence of coordination-relevant transitions

Rule:

- if a state transition affects global coordination or recoverability, it should not rely on unstored session-local knowledge
- if a mutating operation affects live coordination, it should be accepted through daemon logic before becoming authoritative

---

## 3. tmux model

Sessions run inside tmux.

Each primary node session should record:

- session ID
- node version ID
- node run ID
- tmux session name
- provider session ID if available
- working directory
- last heartbeat time
- current compiled subtask ID

tmux requirements:

- a node run must be attachable through tmux
- terminal detach must not lose node state
- host reboot or tmux loss must still allow DB-driven resume or replacement-session recovery

---

## 4. High-level node execution loop

A normal node execution loop is:

1. node run is admitted
2. primary session binds to node run
3. session retrieves compiled workflow and current cursor
4. session retrieves current subtask payload
5. session performs subtask work
6. session records progress through CLI
7. runtime validates results and advances cursor if accepted
8. quality-gate stages run in canonical order
9. when all stages are done, node finalization runs

The loop must remain CLI-driven and inspectable.

---

## 5. Required AI-facing command loop

At minimum the runtime loop should support commands like these.

### Session bootstrap

- `ai-tool session bind --node <id>`
- `ai-tool session show-current`
- `ai-tool workflow current --node <id>`

### Prompt and context retrieval

- `ai-tool subtask current --node <id>`
- `ai-tool subtask prompt --node <id>`
- `ai-tool subtask context --node <id>`

### Progress marking

- `ai-tool subtask start --compiled-subtask <id>`
- `ai-tool subtask heartbeat --compiled-subtask <id>`
- `ai-tool subtask complete --compiled-subtask <id>`
- `ai-tool subtask fail --compiled-subtask <id> --summary-file <path>`

### Summary and artifact registration

- `ai-tool summary register --node <id> --file <path> --type <type>`
- `ai-tool prompts list --node <id>`

### Cursor control

- `ai-tool workflow advance --node <id>`
- `ai-tool workflow pause --node <id>`
- `ai-tool workflow resume --node <id>`

### Recovery

- `ai-tool session nudge --node <id>`
- `ai-tool session resume --node <id>`
- `ai-tool session attach --node <id>`

The command names may evolve, but the behavior must exist.

---

## 6. Canonical node loop pseudocode

```python
def run_node_loop(node_id):
    run = admit_or_load_active_run(node_id)
    session = bind_or_resume_primary_session(run.id)

    while True:
        state = load_run_state(run.id)
        subtask = get_current_compiled_subtask(run.id)

        if subtask is None:
            finalize_completed_workflow(run.id)
            break

        mark_subtask_started(run.id, subtask.id, session.id)
        result = execute_compiled_subtask(run.id, subtask, session.id)

        if result.status == "ok":
            persist_subtask_outputs(run.id, subtask.id, result)
            run_required_validations(run.id, subtask.id, result)
            mark_subtask_complete(run.id, subtask.id)
            advance_cursor(run.id)
            continue

        if result.status == "pause":
            register_summary(node_id, result.summary_path, "pause")
            transition_run_to_paused(run.id, result.pause_flag)
            break

        if result.status == "failed":
            register_summary(node_id, result.summary_path, "failure")
            handle_subtask_failure(run.id, subtask.id, result)
            break
```

This pseudocode is intentionally high-level. The implementation must expand each helper into durable state transitions.

---

## 7. Canonical subtask loop

For each compiled subtask:

1. retrieve current compiled subtask ID
2. retrieve prompt, command, context, and prior results
3. create or update the current subtask attempt
4. mark subtask started
5. perform work
6. persist outputs and summaries
7. run required validations
8. record attempt result
9. either:
   - advance cursor
   - retry
   - pause for user
   - fail to parent

The cursor must advance only after successful completion and accepted validations.

---

## 8. Subtask handler classes

The runtime should dispatch by compiled subtask type.

### Handler families

- `run_prompt`
- `run_command`
- `build_context`
- `wait_for_children`
- `wait_for_sibling_dependency`
- `validate`
- `review`
- `run_tests`
- `build_docs`
- `write_summary`
- `finalize_node`
- `spawn_child_session`
- `spawn_child_node`
- `reset_to_seed`
- `merge_children`
- `update_provenance`

Each handler must define:

- expected inputs
- expected outputs
- failure behavior
- pause behavior if applicable
- validation behavior

---

## 9. Quality-gate runtime ordering

The default built-in runtime order is:

1. reconcile
2. validation
3. review
4. testing
5. provenance update
6. docs build
7. finalize

Runtime rule:

- validation, review, testing, provenance, and docs may compile into ordinary subtasks, but they are still semantically meaningful named stages

### Validation stage

- executes required checks
- records `validation_results`
- blocks advancement on required failure

### Review stage

- builds review input context
- records `review_results`
- decides continue, revise, pause, or fail

### Testing stage

- executes testing definitions
- records `test_results`
- decides continue, fail, or policy-allowed override

### Provenance stage

- refreshes entity and rationale mappings

### Docs stage

- builds local or merged documentation views

---

## 10. Prompt retrieval behavior

Every executable step should be retrievable through CLI rather than only as ephemeral terminal text.

The session should be able to ask for:

- current subtask prompt
- current subtask command
- current subtask context
- previous subtask summaries
- dependency summaries when relevant
- child summaries when relevant
- review/validation/testing results when relevant

This keeps execution restartable and auditable.

---

## 10A. Runtime guidance prompt payloads

The runtime should not rely on improvised operator text when starting, correcting, nudging, or recovering sessions.

The default prompt pack for these payloads lives in `notes/prompt_library_plan.md`.

At minimum the runtime should have authored payloads for:

- initial CLI/bootstrap guidance
- missed-step or validation-failure correction
- command failure correction
- missing-output correction
- idle nudge
- pause-for-user handoff
- resume existing session
- replacement-session bootstrap

### Default CLI/bootstrap payload

```text
You are the active session for node <node_id> and compiled subtask
<compiled_subtask_id>.

Retrieve work with:
- `ai-tool subtask current --node <node_id>`
- `ai-tool subtask prompt --node <node_id>`
- `ai-tool subtask context --node <node_id>`

Use:
- `ai-tool subtask start --compiled-subtask <compiled_subtask_id>`
- `ai-tool subtask heartbeat --compiled-subtask <compiled_subtask_id>`
- `ai-tool subtask complete --compiled-subtask <compiled_subtask_id>`
- `ai-tool subtask fail --compiled-subtask <compiled_subtask_id> --summary-file <summary_path>`

Do not rely on unstored terminal context. The CLI and durable run state are the
authoritative execution contract.
```

### Default missed-step payload

```text
The current stage is not complete yet for node <node_id>.

Missing requirements:
<missing_requirements>

Reload the current prompt/context through CLI, satisfy the missing requirement,
and only then mark the stage complete.

If you cannot satisfy the requirement safely, fail the subtask with a concise
summary instead of waiting idle.
```

---

## 11. Subtask attempt ownership

The runtime must make the subtask-attempt lifecycle explicit.

### Attempt lifecycle

1. create attempt row
2. mark started
3. collect heartbeats while active
4. capture outputs and changes
5. capture validations and summaries
6. mark terminal status

### Ownership rule

The session may initiate progress commands, but the durable acceptance of completion should be runtime-validated against the compiled workflow and required checks.

This prevents cursor corruption from incomplete or invalid session-side assumptions.

---

## 12. Pause and gating behavior

When a subtask or stage encounters a user gate:

1. complete the current durable attempt state
2. register a pause summary
3. set `pause_flag_name`
4. transition the run to `PAUSED_FOR_USER`
5. expose the pause reason through CLI

Resume requires:

- clearing or approving the gate
- restoring the same compiled workflow and cursor
- continuing from the correct post-gate stage

The runtime must not silently skip a user gate on resume.

---

## 13. Failure handling

When a subtask fails:

1. classify the failure
2. record a failure summary
3. evaluate retry policy
4. either:
   - retry the current subtask
   - pause for the user
   - fail the node to parent

### Retry rule

Retries should be driven by compiled retry policy, not by ad hoc session behavior.

### Parent escalation rule

If the node fails upward:

1. the child records `FAILED_TO_PARENT`
2. the parent increments child-failure counters
3. the parent decides whether to retry, replan, pause, or fail further upward

This decision path must be durable and inspectable.

Recommended default parent decision order:

1. record the failure impact durably in parent context
2. classify the failure
3. evaluate hard-stop thresholds
4. retry the child if the failure is retryable and budget remains
5. regenerate the child version if retry is insufficient but parent assumptions remain valid
6. revise or replan locally at the parent if the failure indicates bad inputs, bad layout, or impossible requirements
7. pause for the user if ambiguity or safety thresholds prevent autonomous handling
8. fail upward only through the parent's own resulting failure path

---

## 14. Child node orchestration

Child-node work is different from pushed child sessions.

### Child-node lifecycle

1. materialize layout-defined children
2. persist child node versions
3. persist child dependency edges
4. schedule any ready children
5. wait for dependencies or completion as needed
6. collect child summaries and child final outputs
7. reconcile parent

### Runtime rules

- child nodes own their own runs and sessions
- parent nodes do not share cursor ownership with children
- parent nodes may query child state through CLI and DB

### Scheduling rule

Any child whose dependencies are satisfied should be eligible to start immediately.

---

## 15. Pushed child session behavior

### Push

Command shape:

- `ai-tool session push --node <id> --reason <reason>`

Push should:

- create a child session record
- snapshot bounded parent context
- launch isolated child session context
- preserve parent cursor without advancing it

### Child session work

The pushed child session performs focused work and ends by producing a summary or artifact set for the parent.

The child session should return a structured result contract that includes at minimum:

- child session ID
- parent compiled subtask ID
- outcome status such as `success|partial|failed`
- summary text
- referenced artifacts if any
- suggested next actions if relevant

### Pop

Command shape:

- `ai-tool session pop --session <id> --summary-file <path>`

Pop should:

- persist child-session summary
- validate the returned result structure
- attach the summary to parent subtask context
- mark child session complete
- return control to the parent session

After merge-back:

- the parent resumes at the same compiled subtask it was on before the push
- the parent runtime decides whether the returned result is sufficient to continue or whether the parent subtask should retry, revise, fail, or pause

This is for context isolation only. The parent node remains the owner of git state and workflow progress.

---

## 16. Recovery and resume behavior

If a run is interrupted:

1. inspect `node_runs`, `node_run_state`, `sessions`, and current git state
2. determine whether the bound primary session is still recoverable
3. if recoverable, reattach or resume it
4. if not recoverable, create a replacement session
5. reload compiled workflow and current cursor
6. continue from the current compiled subtask

### Recovery priorities

1. preserve durable cursor correctness
2. preserve session continuity when possible
3. avoid duplicate active primary sessions
4. avoid losing the current subtask attempt history

Recommended recovery scenarios to distinguish explicitly:

- healthy attached session
- healthy detached session
- stale session with live tmux
- lost tmux with recoverable run
- provider session available but tmux lost
- resumable run with no viable session
- non-resumable run
- git state mismatch
- duplicate active primary sessions

### Provider-agnostic rule

If provider session identity is unavailable or unreliable, recovery should still work using:

- node run state
- tmux session state if available
- branch/head state
- compiled workflow and attempt history

If provider or tmux state conflicts with durable run state, the durable run state is authoritative unless the runtime explicitly proves it is stale.

---

## 17. Idle detection and nudge behavior

If a session goes idle unexpectedly:

1. detect missing or stale heartbeat
2. inspect current run state
3. reissue current subtask summary and context
4. remind the session how to complete or fail the stage
5. record a nudge event

The nudge payload should include:

- current subtask title
- prompt or command summary
- expected completion command
- expected failure-summary command

Repeated idle behavior should be bounded by runtime policy and may escalate into:

- another nudge
- pause for user
- failure handling

Recommended workflow-event scope for first implementation:

- pause entered/cleared
- recovery attempted/succeeded/failed
- replacement session created
- parent decision events
- cutover events

---

## 18. Compilation boundary and runtime policy

The runtime must respect the compile boundary.

Compiled workflow includes:

- resolved tasks and subtasks
- hooks
- validations
- selected review/testing/docs stages
- dependency graph

Pure runtime policy may remain outside compiled workflow if it does not change semantic workflow behavior.

Examples of likely runtime policy:

- heartbeat interval
- idle timeout
- maximum nudge count

If a policy changes stage structure or gating behavior, it must be part of compiled workflow lineage.

---

## 19. Rectification command loop behavior

Rectification should use the same durable execution model as normal runs.

### Rectification loop

1. create or load rectification run
2. bind primary session
3. execute reset-to-seed stage
4. execute merge-children stage
5. execute reconcile stage
6. execute validation, review, testing, provenance, docs, and finalize stages
7. if successful, continue upstream rectification if required

### Conflict handling

If merge conflict occurs:

1. persist merge-conflict record
2. transition into reconcile/conflict-resolution stage
3. if resolved, continue the quality-gate pipeline
4. if unresolved, fail to parent or pause for user according to policy

---

## 20. Required operator surfaces for runtime debugging

Operators and AI sessions should be able to inspect:

- current run state
- current compiled subtask
- current subtask attempt
- active primary session
- pushed child sessions
- validation/review/testing results
- dependency blockers
- active pause reason
- recent session events
- recent summaries

No critical runtime variable should be hidden only in process memory.

---

## 21. Operational rule

A node run must always be reconstructible from:

- source YAML and overrides as of compilation time
- compiled workflow snapshot
- current cursor state
- prior subtask attempts
- session records and events
- quality-gate results
- summaries
- git seed/head/final lineage

If the runtime cannot reconstruct execution from those artifacts, it is violating the model.

---

## 22. V2 closure notes

This V2 runtime loop spec resolves or reduces the following prior gaps:

- clearer actor ownership between session, runtime, and durable state
- clearer integration of review/testing/docs into the runtime loop
- clearer recovery and nudge behavior
- clearer distinction between child nodes and pushed child sessions

Remaining follow-on work still needed:

- fold the child-session result contract into final DB and CLI implementation details
- wire the frozen minimum workflow-event set for pause, recovery, parent decisions, and cutover into implementation-grade runtime, DB read-model, and CLI planning
- align implementation slicing with the current authority and recovery model
