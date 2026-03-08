# Runtime Command Loop Spec

## Purpose

This document defines the AI-facing execution loop for nodes, subtasks, tmux-backed sessions, optional pushed child sessions, and CLI interactions.

This is the missing operational layer between:

- compiled node workflows in the database
- tmux-backed AI sessions
- CLI-driven state updates
- resume/nudge/error-summary behavior

Design goal:

- the same CLI should serve both operators and AI sessions
- no critical runtime state should exist only in memory
- every node run should be resumable from durable state

---

## 1. Core runtime model

### Primary rule

Default behavior:

- one node run uses one primary AI session

That means:

- one node version
- one active node run
- one primary session binding
- one compiled workflow cursor

### Optional pushed child session

A subtask may optionally run in a temporary child session when bounded isolation of context is useful.

Examples:

- research
- review
- verification
- focused search/summarization

This push/pop mechanism is for context management only.

It does **not** transfer:

- node ownership
- git ownership
- branch ownership
- compiled workflow ownership

The parent session remains the owner of node execution.

---

## 2. tmux model

Sessions are run inside tmux.

Each primary node session should record:

- session ID
- node version ID
- node run ID
- tmux session name
- working directory
- provider session ID if available
- last heartbeat time
- current compiled subtask ID

### tmux requirements

- a node run must be attachable through tmux
- loss of terminal attachment must not lose node state
- host reboot or tmux crash should still allow resume from DB state and git state

---

## 3. High-level node execution loop

A normal node execution loop is:

1. node run starts
2. session binds to node run
3. session retrieves compiled workflow and current cursor
4. session retrieves current subtask payload
5. session performs subtask work
6. session records progress through CLI
7. if subtask succeeds, cursor advances
8. if subtask fails, failure is recorded and parent-facing policy is applied
9. when all subtasks are done, node finalization and completion logic runs

The loop must be CLI-driven and inspectable.

---

## 4. Required AI-facing command loop

At minimum the runtime loop should support commands like these.

### Session bootstrap

- `ai-tool session bind --node <id>`
- `ai-tool session show-current`
- `ai-tool workflow current --node <id>`

### Prompt / subtask retrieval

- `ai-tool subtask current --node <id>`
- `ai-tool subtask prompt --node <id>`
- `ai-tool subtask context --node <id>`

### Progress marking

- `ai-tool subtask start --compiled-subtask <id>`
- `ai-tool subtask heartbeat --compiled-subtask <id>`
- `ai-tool subtask complete --compiled-subtask <id>`
- `ai-tool subtask fail --compiled-subtask <id> --summary-file <path>`

### Summary/reporting

- `ai-tool summary register --node <id> --file <path> --type <type>`
- `ai-tool prompt-history show --node <id>`

### Cursor control

- `ai-tool workflow advance --node <id>`
- `ai-tool workflow pause --node <id>`
- `ai-tool workflow resume --node <id>`

### Recovery

- `ai-tool session nudge --node <id>`
- `ai-tool session resume --node <id>`
- `ai-tool session attach --node <id>`

The exact names can change, but this command loop behavior should exist.

---

## 5. Canonical subtask loop

For each compiled subtask:

1. retrieve current compiled subtask ID
2. retrieve prompt/command/context
3. mark subtask started
4. perform work
5. persist any generated summary or artifacts
6. run required validations or record validation results
7. mark subtask complete or failed
8. advance cursor only if completion was accepted

### Pseudocode

```python
def run_node_loop(node_id):
    session_bind(node_id)

    while True:
        subtask = cli.get_current_subtask(node_id)
        if subtask is None:
            finalize_node(node_id)
            break

        cli.mark_subtask_started(subtask.id)
        result = execute_subtask(subtask)

        if result.status == "ok":
            if result.summary_path:
                cli.register_summary(node_id, result.summary_path, "subtask")
            cli.mark_subtask_complete(subtask.id)
            cli.advance_workflow(node_id)
        else:
            if result.summary_path:
                cli.register_summary(node_id, result.summary_path, "failure")
            cli.mark_subtask_failed(subtask.id, result.summary_path)
            break
```

---

## 6. Prompt retrieval behavior

Every executable step should be retrievable through CLI rather than being passed only as ephemeral terminal text.

The AI session should be able to ask for:

- current subtask prompt
- current subtask command
- current subtask context
- previous subtask result summaries
- child/sibling dependency summaries if relevant

This keeps execution restartable and auditable.

---

## 7. Idle detection and nudge behavior

If a session goes idle unexpectedly:

1. detect stale heartbeat
2. inspect current compiled subtask
3. reissue the current subtask prompt and context
4. remind the session how to register a summary if blocked or stuck
5. do not silently advance the cursor

The nudge should include:

- current subtask title
- current prompt or command summary
- expected completion command
- expected failure-summary command

This directly matches the intended “repeat the last stage and remind it how to register a summary” behavior.

---

## 8. Push/pop child session behavior

### Push

A parent session may push a child session for a bounded subtask.

Command shape:

- `ai-tool session push --node <id> --reason <reason>`

Push should:

- create child session record
- snapshot parent context for the pushed subtask
- launch new isolated AI session context
- preserve parent cursor without advancing it

### Child session work

The child session performs focused work and must end by writing a summary back.

### Pop

Command shape:

- `ai-tool session pop --session <id> --summary-file <path>`

Pop should:

- persist child summary
- attach summary to parent subtask context
- mark child session complete
- return control to parent session

This is for context management only. Parent node git state remains authoritative.

---

## 9. Failure behavior in the command loop

Failure is parent-facing.

If a subtask cannot proceed:

1. AI writes a structured summary
2. AI runs failure command
3. runtime records failure on current compiled subtask
4. node transitions to `FAILED_TO_PARENT`
5. parent failure threshold logic decides next step

Recommended structured failure payload:

```json
{
  "status": "FAILED_TO_PARENT",
  "reason": "Could not complete validation because required interface contract is missing.",
  "recommended_next_action": "Parent should revise child plan or provide additional context.",
  "artifacts": [".ai/failure_summary.md"]
}
```

---

## 10. Resume behavior

Resume order should be:

1. recover provider-native session if possible
2. otherwise reattach tmux if still alive
3. otherwise start a fresh session in the same working directory
4. reload node run state from DB
5. restore current compiled subtask
6. continue the loop

Provider-native resume is an optimization, not the source of truth.

The source of truth is:

- DB state
- compiled workflow
- git state
- stored summaries and prompts

---

## 11. Session summary requirements

Every session, including pushed child sessions, should be able to register summaries for:

- normal completion
- partial completion
- blocked state
- failure
- research findings
- review findings

This should be a first-class operation, not a side effect.

---

## 12. Runtime-visible state that must be queryable

The command loop relies on the ability to query:

- current node run
- current compiled subtask
- subtask history
- retry count
- current prompt
- current context bundle
- seed/final commit state
- session binding
- last heartbeat
- child failure counters
- pause flags and user-gating flags

No part of the loop should depend on invisible mutable memory inside the runner.

---

## 13. User gating / pause flags

Tasks and subtasks should support pause points that defer to user before continuing.

A useful model is:

- `block_on_user_flag: <flag_name>`
- `pause_summary_prompt: <text or reference>`

Behavior:

1. subtask completes
2. cursor advances to next subtask
3. runtime checks whether the next subtask is gated by a user flag
4. if gated, runtime immediately transitions node run into paused-for-user state instead of executing the next subtask
5. runtime generates or records a summary explaining what is waiting and why

This should also support user-gated top-node merge-to-base behavior.

---

## 14. Concurrency model

Any node whose dependencies are satisfied should be eligible to start immediately.

That means:

- sibling nodes with no unmet dependencies should run concurrently
- child groups should run concurrently where possible
- parent nodes should wait only on explicitly required child/sibling dependencies

The command loop should therefore be safe under multi-session concurrent execution across many nodes.

---

## 15. Final rule

The runtime command loop is the operational protocol binding together:

- AI sessions
- tmux
- compiled workflows
- CLI operations
- durable database state

If the AI cannot recover its current subtask, report progress, register summaries, and resume through CLI alone, the runtime model is incomplete.

