# Node Lifecycle Spec

## Purpose

This document defines the runtime lifecycle for nodes in the hierarchy.

In this system:

- a **node** is the durable execution context
- nodes are organized by configurable **tiers**, not by a hardcoded hierarchy
- a **task** is a phase of node execution that runs a list of subtasks
- a **subtask** is one executable stage inside a task
- subtasks may call subtasks
- tasks may call subtasks
- tasks may not call tasks
- subtasks may not call tasks

The lifecycle must be durable, introspectable, resumable, and safe against later YAML edits.

---

## 1. Core terminology

### Node
A durable unit with its own branch, run history, prompts, documentation, and state.

### Tier
A configurable hierarchy level declared in YAML. Tiers are not hardcoded. Multiple node kinds may exist at the same tier.

### Node kind
A semantic label such as `epic`, `phase`, `plan`, `task`, or any future user-defined kind.

### Task
A named execution phase owned by a node definition. A task runs an ordered list of subtasks.

### Subtask
A compiled executable stage inside a task. Subtasks are the unit of step-by-step execution and introspection.

### Compiled workflow
An immutable expanded snapshot created when a node version is created. This snapshot is persisted in the database and used for execution so later YAML changes do not silently alter in-flight or historical runs.

### Node version
A durable version of a node. Regeneration creates a new node version rather than mutating an old one in place.

### Node run
One execution attempt for one node version.

### Seed commit
The git commit representing the node's starting state before its current child generation/merge cycle.

### Final commit
The git commit that represents the completed output of the node version.

---

## 2. Hierarchy model

The hierarchy is not fixed to `epic -> phase -> plan -> task`.

Instead, each node definition declares:

- a `tier`
- a node kind
- any constraints on allowed parent/child relationships

A common default ladder may be:

- epic
- phase
- plan
- task

but this is only a convention, not a runtime restriction.

Rules:

- every node has at most one parent
- only a top node lacks a parent
- subtasks are not tree nodes
- sibling and child dependencies are allowed
- parent, cousin, and more distant dependency edges are not allowed
- any node whose dependencies are satisfied should be eligible to start immediately

Manual tree construction must be supported. A user may create a node at any tier, including a parentless top node, and define its children manually instead of relying on automatic decomposition.

A parentless top node should be able to complete independently and then wait for explicit user approval before any merge back into base.

---

## 3. Node identity and required runtime metadata

Each node version should persist at minimum:

- `node_id`
- `node_version_id`
- `parent_node_id` nullable
- `tier`
- `node_kind`
- `title`
- `description`
- `status`
- `branch_name`
- `seed_commit_sha`
- `final_commit_sha` nullable until completion
- `compiled_workflow_id`
- `active_run_id` nullable
- `supersedes_node_version_id` nullable

The runtime system should also be able to derive:

- full ancestor chain
- child list
- sibling list
- dependency satisfaction
- current compiled subtask pointer
- accumulated prior subtask results

A node should not require the full top-node context to execute. Runtime systems may traverse upward and back down when needed rather than precomputing broad traversal hints into prompts.

---

## 4. Compiled workflow model

A node should not execute directly from mutable YAML files.

Instead:

1. load source YAML and applicable overrides
2. resolve hooks and project policies
3. validate against schemas
4. compile an immutable workflow snapshot
5. persist compiled stages with durable IDs
6. execute from the compiled snapshot

This solves several problems:

- historical runs remain repeatable
- later YAML edits do not corrupt existing node runs
- subtask introspection becomes stable and queryable
- stage-level resume is straightforward

### Compiled workflow contents

A compiled workflow should include:

- node version ID
- source definition references and content hashes
- fully expanded task list
- fully expanded ordered subtask list within each task
- durable compiled subtask instance IDs
- dependency edges between compiled subtasks
- resolved commands and prompts
- resolved hook insertions
- validation checks
- retry policies
- user-gating flags
- escalation policies

---

## 5. Execution state model

The node state needs to be richer than a simple lifecycle enum.

There should be two layers of state.

### A. Node lifecycle state

Recommended values:

- `DRAFT`
- `COMPILED`
- `READY`
- `RUNNING`
- `WAITING_ON_CHILDREN`
- `WAITING_ON_SIBLING_DEPENDENCY`
- `RECTIFYING_SELF`
- `RECTIFYING_UPSTREAM`
- `REVIEW_PENDING`
- `VALIDATION_PENDING`
- `FAILED_TO_PARENT`
- `PAUSED_FOR_USER`
- `COMPLETE`
- `SUPERSEDED`
- `CANCELLED`

### B. Run execution state

Recommended fields:

- `current_task_id`
- `current_compiled_subtask_id`
- `current_subtask_attempt`
- `last_completed_subtask_id`
- `execution_cursor_json`
- `failure_count_from_children`
- `defer_to_user_threshold`
- `is_resumable`
- `session_id`
- `working_tree_state`
- `pause_flag_name` nullable

Both layers must be durable.

---

## 6. Compiled subtask tracking

Each compiled subtask instance should have:

- durable compiled subtask ID
- parent compiled workflow ID
- parent task ID
- source subtask key from YAML
- ordinal position
- type
- resolved prompt text
- resolved command text
- dependency list
- retry policy
- block-on-user metadata
- inserted-by-hook metadata
- source file and source hash

Each execution attempt of a compiled subtask should record:

- compiled subtask ID
- attempt number
- start time
- end time
- input snapshot
- output snapshot
- changed files
- git head before
- git head after
- validation results
- summary
- status

This allows:

- exact introspection of what a node did
- stable references even if YAML changes later
- targeted resume from the current compiled subtask

---

## 7. Lifecycle transitions

### Primary node transitions

- `DRAFT -> COMPILED`
- `COMPILED -> READY`
- `READY -> RUNNING`
- `RUNNING -> WAITING_ON_CHILDREN`
- `RUNNING -> WAITING_ON_SIBLING_DEPENDENCY`
- `RUNNING -> RECTIFYING_SELF`
- `RUNNING -> VALIDATION_PENDING`
- `RUNNING -> REVIEW_PENDING`
- `RUNNING -> FAILED_TO_PARENT`
- `FAILED_TO_PARENT -> PAUSED_FOR_USER`
- `RUNNING -> COMPLETE`
- `COMPLETE -> RECTIFYING_UPSTREAM`
- `RECTIFYING_UPSTREAM -> COMPLETE`
- `COMPLETE -> SUPERSEDED`
- `READY -> CANCELLED`
- `RUNNING -> CANCELLED`

### Regeneration transitions

When a node or its specification changes:

1. create a new node version
2. compile a new immutable workflow snapshot
3. regenerate affected descendants if required by the node definition
4. rebuild the node from seed
5. rebuild ancestors from seed up to the top node
6. mark prior version superseded only after the new lineage is stable

---

## 8. Failure policy

Failure should escalate only to the parent.

When a child fails:

1. it records a structured failure summary
2. it marks itself `FAILED_TO_PARENT`
3. its parent increments child-failure counters
4. the parent decides whether to retry, replan locally, or defer to user

Each node should have user-configurable thresholds such as:

- `child_failure_threshold_total`
- `child_failure_threshold_consecutive`
- `child_failure_threshold_per_child`

Once threshold is exceeded:

- parent transitions to `PAUSED_FOR_USER`
- parent emits a structured summary explaining:
  - which children failed
  - which subtasks failed
  - what retries were attempted
  - likely root causes
  - recommended next actions

This preserves parent-only escalation while still allowing the effect to cascade upward through repeated parent decisions.

---

## 9. Session model and resume model

Default rule:

- one node run corresponds to one primary AI session

Optional extension:

- a subtask may push into a temporary child session for bounded work such as research, review, or verification
- when that child session completes, it must summarize its result and hand that summary back into the parent session before the parent resumes
- this push/pop behavior is for context management, not git ownership
- the parent node remains the owner of git state and the compiled workflow cursor

Resume requires:

- compiled workflow snapshot
- current compiled subtask pointer
- prior subtask results
- active or recoverable session binding
- current git branch and head

If runtime is interrupted:

1. recover session if possible
2. otherwise start a new session
3. reload compiled workflow and execution cursor
4. continue from the current compiled subtask

---

## 10. Required introspection surfaces

Every major lifecycle variable should be queryable through CLI.

At minimum, operators and AI sessions should be able to inspect:

- node lifecycle state
- active run state
- compiled workflow
- current task pointer
- current subtask pointer
- subtask execution history
- retry counts
- parent failure counters
- seed and final commits
- hook insertions
- session binding
- latest summaries
- pause flags and gating points

No critical runner state should be hidden only in memory.

---

## 11. Core rule

A node version must be fully reconstructible from:

- source YAML plus overrides as of compilation time
- compiled workflow snapshot
- current child final commits
- seed commit
- persisted subtask execution data
- persisted hooks, validation, and review results

