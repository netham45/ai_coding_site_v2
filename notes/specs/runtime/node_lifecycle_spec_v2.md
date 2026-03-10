# Node Lifecycle Spec V2

## Purpose

This document defines the canonical runtime lifecycle for nodes in the hierarchy.

V2 expands the prior lifecycle spec by:

- aligning lifecycle behavior with the v2 YAML and DB models
- freezing the default quality-gate ordering
- clarifying pause, failure, and parent-escalation behavior
- clarifying supersession and rebuild cutover expectations
- clarifying session and resume assumptions

In this system:

- a **node** is the durable execution context
- nodes are organized by configurable **tiers**
- a **task** is a named execution phase owned by a node definition
- a **subtask** is one executable stage inside a task
- execution runs from immutable compiled workflows

Authority model:

- the daemon is the live orchestration authority
- the database is the durable canonical record
- lifecycle transitions should be decided by daemon logic and then persisted durably

---

## 1. Core terminology

### Node

A durable unit with its own branch, run history, prompts, summaries, docs, and state.

### Tier

A configurable hierarchy level declared in YAML. Tiers are not hardcoded.

### Node kind

A semantic label such as `epic`, `phase`, `plan`, `task`, or any future user-defined kind.

### Task

A named execution phase owned by a node definition. A task runs an ordered list of compiled subtasks.

### Subtask

A compiled executable stage inside a task. Subtasks are the unit of step-by-step execution and introspection.

### Compiled workflow

An immutable expanded snapshot created by the workflow compiler for a specific node version.

Implementation staging note:

- current node creation and supersede flows capture source lineage immediately
- immutable workflow creation now occurs on the explicit compile path rather than automatically at node/version creation time
- the current top-level startup surface now bridges those steps explicitly: `workflow start` creates the node at `DRAFT`, compiles it, transitions it to `READY`, and optionally admits the first run immediately

### Node version

A durable version of a node. Regeneration creates a new node version rather than mutating an old one.

### Node run

One execution attempt for one node version.

### Seed commit

The git commit representing the node's starting state before its child-merge and node-local reconciliation cycle.

### Final commit

The git commit representing the completed output of the node version.

---

## 2. Hierarchy model

The hierarchy is not fixed to `epic -> phase -> plan -> task`.

Instead, each node definition declares:

- `tier`
- `kind`
- optional parent constraints
- optional child constraints

Rules:

- every node has at most one parent
- only a top node lacks a parent
- subtasks are not tree nodes
- sibling and child dependencies are allowed
- parent, cousin, and more distant dependency edges are not allowed
- any node whose dependencies are satisfied should be eligible to start

Clarification:

- top-ness is structural, not semantic
- any node kind may be a top node if it is created without a parent and its hierarchy definition allows `allow_parentless: true`
- `epic`, `phase`, `plan`, and `task` are semantic defaults, not exclusive top-level privileges

Manual tree construction must be supported. A user may create a node at any tier and define children manually rather than relying only on automatic decomposition.

If manual and layout-generated children coexist under one parent, the system should treat that child set as structurally hybrid rather than silently allowing one authority model to overwrite the other.

Implementation staging note:

- the current implementation now persists parented manual node creation through `node_children` with `origin_type = manual`
- a parent with only manually inserted durable children is treated as `manual`
- adding a manual child to a previously layout-authoritative parent now flips the parent to `hybrid`

---

## 3. Compiled workflow model

A node must not execute directly from mutable YAML files.

Instead:

1. load source YAML and applicable overrides
2. validate against schemas
3. resolve policies and hooks
4. compile an immutable workflow snapshot
5. persist compiled tasks, subtasks, checks, and dependencies
6. execute from the compiled snapshot

This ensures:

- historical runs remain repeatable
- later YAML edits do not alter in-flight history
- subtask introspection is stable
- resume behavior is reconstructible

Compiled workflow durability does not remove daemon ownership of live coordination.

The runtime should execute from compiled artifacts under daemon control and persist each coordination-relevant transition durably.

Implementation staging note:

- stage startup context is now derived from durable node/run/history state rather than terminal history
- the current daemon assembles a repeatable context bundle from node-version startup metadata, current compiled-subtask metadata, dependency state, recent prompt/summary history, and cursor-carried reconcile/child-session state
- the same assembled bundle is exposed through both `subtask prompt` and `subtask context`, and `subtask context` mirrors it inside `input_context_json.stage_context_json` for compatibility with older context consumers
- this stage-context bundle remains a derived read model, not a separate durable authority; the canonical inputs remain node/run/workflow/history tables plus run-cursor overlays

---

## 4. Required node metadata

Each node version must persist at minimum:

- `node_version_id`
- `logical_node_id`
- `parent_node_version_id`
- `tier`
- `node_kind`
- `title`
- `description`
- `status`
- `branch_name`
- `seed_commit_sha`
- `final_commit_sha`
- `compiled_workflow_id`
- `supersedes_node_version_id`

The runtime must also be able to derive:

- ancestor chain
- child list
- sibling list
- dependency readiness
- current run
- current task pointer
- current subtask pointer
- prior subtask results

---

## 5. Lifecycle state model

The node state needs two durable layers.

## A. Node lifecycle state

Recommended values:

- `DRAFT`
- `COMPILE_FAILED`
- `COMPILED`
- `READY`
- `RUNNING`
- `WAITING_ON_CHILDREN`
- `WAITING_ON_SIBLING_DEPENDENCY`
- `RECTIFYING_SELF`
- `RECTIFYING_UPSTREAM`
- `REVIEW_PENDING`
- `VALIDATION_PENDING`
- `TESTING_PENDING`
- `PAUSED_FOR_USER`
- `FAILED_TO_PARENT`
- `COMPLETE`
- `SUPERSEDED`
- `CANCELLED`

## B. Run execution state

Recommended fields:

- `current_task_id`
- `current_compiled_subtask_id`
- `current_subtask_attempt`
- `last_completed_compiled_subtask_id`
- `execution_cursor_json`
- `failure_count_from_children`
- `failure_count_consecutive`
- `defer_to_user_threshold`
- `is_resumable`
- `pause_flag_name`
- `working_tree_state`

Both layers must be durable and queryable.

Implementation staging note:

- the current implementation persists these fields in a durable `node_lifecycle_states` table even before immutable compiled workflows and full node-version lineage are implemented
- hierarchy-created nodes are seeded at `DRAFT`
- daemon-started legacy nodes that do not yet have a lifecycle row are temporarily bootstrapped through `READY` so pre-versioned authority tests and simple operational commands can still exercise run admission
- this bootstrap path should be removed once node versioning and compiled workflow admission become authoritative
- node lifecycle is still currently keyed by logical node id rather than node version id, so version cutover changes the current authoritative version selector without yet preserving separate lifecycle rows per historical version

---

## 6. Quality-gate ordering

The default built-in quality-gate ordering is:

1. reconcile node-local output
2. validation
3. review
4. testing
5. provenance update
6. docs build
7. finalize node

Reasoning:

- validation should reject obviously invalid state early
- review should examine semantically valid output before heavier test execution
- testing should gate final artifact generation
- provenance should run before docs so docs can consume updated code/rationale data
- docs should build before finalization so final node state includes generated documentation outputs

Projects may override this ordering only where policy and runtime semantics explicitly allow it.

---

## 7. Compiled subtask tracking

Each compiled subtask instance should have:

- durable compiled subtask ID
- parent compiled workflow ID
- parent task ID
- source subtask key
- ordinal position
- type
- resolved prompt and command text
- dependency list
- retry policy
- block-on-user metadata
- inserted-by-hook metadata
- source file path and source hash

Each execution attempt should record:

- compiled subtask ID
- attempt number
- start and end time
- input snapshot
- output snapshot
- changed files
- git head before and after
- validation results
- summary
- status

---

## 8. Primary lifecycle transitions

Recommended high-level transitions:

- `DRAFT -> COMPILED`
- `DRAFT -> COMPILE_FAILED`
- `COMPILE_FAILED -> COMPILED`
- `COMPILED -> READY`
- `READY -> RUNNING`
- `RUNNING -> WAITING_ON_CHILDREN`
- `RUNNING -> WAITING_ON_SIBLING_DEPENDENCY`
- `RUNNING -> VALIDATION_PENDING`
- `VALIDATION_PENDING -> REVIEW_PENDING`
- `REVIEW_PENDING -> TESTING_PENDING`
- `TESTING_PENDING -> RUNNING`
- `RUNNING -> PAUSED_FOR_USER`
- `RUNNING -> FAILED_TO_PARENT`
- `RUNNING -> COMPLETE`
- `COMPLETE -> RECTIFYING_UPSTREAM`
- `RECTIFYING_UPSTREAM -> COMPLETE`
- `COMPLETE -> SUPERSEDED`
- `READY -> CANCELLED`
- `RUNNING -> CANCELLED`

### Notes

- some of these may be represented as current-state fields and not separate workflow engine states, but the lifecycle model must still support the semantics
- `VALIDATION_PENDING`, `REVIEW_PENDING`, and `TESTING_PENDING` may be entered explicitly or treated as visible subtask-owned phases depending on implementation

---

## 9. Run admission rules

A node is eligible to start only if:

- it has a compiled workflow
- its lifecycle state is compatible with running
- required dependencies are satisfied
- it is not blocked on a user gate
- it does not have an incompatible active run already in progress

The default non-runnable lifecycle states include:

- `DRAFT`
- `COMPILE_FAILED`
- `SUPERSEDED`
- `CANCELLED`

If dependencies are not satisfied:

- the node must not run
- the reason should be queryable
- the node may remain `READY`, or transition into a waiting state depending on runtime policy

---

## 10. Pause and user-gating behavior

Tasks and subtasks may define:

- `block_on_user_flag`
- `pause_summary_prompt`

Behavior:

1. the current subtask completes or reaches its gating point
2. a summary is registered for the user
3. the runtime records the active pause flag
4. the node transitions to `PAUSED_FOR_USER`
5. execution does not continue until the gate is cleared

The system should be able to show:

- why the node is paused
- which flag is active
- what summary was produced for the user

If multiple gate conditions exist, the runtime must choose one canonical active pause reason or record them durably in a way the user can inspect.

Recommended direction:

- preserve one canonical active pause reason in current-state surfaces
- preserve pause and gating history durably through dedicated event or history structures

That keeps operational queries simple without losing auditability.

---

## 11. Failure policy

Failure should escalate only to the parent.

When a subtask fails:

1. the runtime records a structured failure summary
2. retry policy is evaluated
3. if retry is allowed, a new subtask attempt is created
4. if retry is exhausted or bypassed, the node records `FAILED_TO_PARENT`
5. the parent increments failure counters and decides next action

When a child fails:

1. the child records `FAILED_TO_PARENT`
2. the parent records the failure impact
3. the parent updates total, consecutive, and per-child failure counters
4. the parent decides whether to:
   - retry or regenerate the child
   - revise its own plan/layout
   - pause for the user
   - fail upward later through its own resulting failure

Thresholds should include:

- `child_failure_threshold_total`
- `child_failure_threshold_consecutive`
- `child_failure_threshold_per_child`

Once a parent exceeds threshold:

- it should transition to `PAUSED_FOR_USER` by default
- it should produce a structured summary listing failed children, retries, likely root causes, and recommended actions

Recommended default parent decision order:

1. record failure impact and increment counters
2. classify the child failure
3. check hard-stop thresholds
4. retry child if safe and budget remains
5. regenerate child if safe and local child state appears stale
6. replan at parent if the failure appears structural
7. otherwise pause for user

Recommended parent decision order:

1. record the child failure impact durably
2. classify the failure
3. check hard-stop thresholds
4. retry the child if the failure class and budget allow it
5. regenerate the child version if retry is insufficient but parent assumptions still appear valid
6. revise or replan locally at the parent if the failure suggests bad inputs or bad layout
7. pause for the user if ambiguity or thresholds prevent safe autonomous handling
8. fail upward later only through the parent becoming the failing node itself

Implementation staging note:

- parent failure handling is now daemon-owned and durable for the first recovery loop
- `retry_child` currently resets the failed child's lifecycle and authority mirror back to `READY` without auto-starting a replacement run
- `replan_parent` currently pauses the parent with `pause_flag_name = parent_replan_required`
- threshold exhaustion currently pauses the parent with `pause_flag_name = parent_child_failure_pause`

Representative failure classes include:

- `transient_execution_failure`
- `validation_failure`
- `review_failure`
- `test_failure`
- `merge_conflict_unresolved`
- `bad_layout_or_bad_requirements`
- `dependency_or_context_failure`
- `environment_failure`
- `unknown_failure`

---

## 12. Session model and resume behavior

Default rule:

- one node run corresponds to one primary session

Optional extension:

- a subtask may push into a temporary child session for bounded work such as research, review, or verification
- pushed child sessions do not own the node branch or workflow cursor

Resume requires:

- compiled workflow snapshot
- current compiled subtask pointer
- prior subtask results
- recoverable or replaceable session binding
- current branch/head knowledge

If runtime is interrupted:

1. inspect durable node/run/session state
2. recover the existing session if possible
3. otherwise create a replacement session
4. reload compiled workflow and cursor
5. continue from the current compiled subtask

No resume-critical state should exist only in transient terminal output.

Recovery should be driven first by durable orchestration state, not by fragile external session state.

Recommended recovery priority order:

1. preserve correct cursor state
2. avoid duplicate active primary sessions
3. reuse an existing valid session when safely possible
4. create a replacement session when reuse is unsafe or impossible

---

## 13. Idle detection and nudge behavior

If a session goes idle unexpectedly:

1. detect stale heartbeat
2. inspect current compiled subtask
3. reissue the current prompt or command summary
4. remind the session how to mark completion or failure
5. do not advance the cursor automatically

The nudge should include:

- current subtask title
- current work summary
- expected completion command
- expected failure-summary command

Repeated idle behavior should be bounded by policy and may eventually escalate to user pause or failure depending on runtime configuration.

Implementation staging note:

- the current daemon now classifies screen state as `active`, `quiet`, or `idle` using pane-hash comparisons plus idle-threshold timing
- `quiet` covers unchanged panes below the idle threshold and alt-screen suppression cases
- only the `idle` classification feeds bounded nudge/escalation behavior

---

## 14. Child node orchestration lifecycle

When a node creates children:

1. the layout is materialized into child node versions
2. child dependency edges are persisted
3. eligible children may start immediately
4. the parent waits on blocked children or dependencies as needed
5. when required children complete, the parent continues into reconciliation

The parent must be able to inspect:

- which children exist
- which are ready
- which are blocked
- which failed
- which final outputs are available for merge/reconcile

---

## 15. Validation, review, and testing lifecycle

Validation, review, and testing are explicit lifecycle stages, whether modeled as dedicated states or dedicated compiled subtasks.

### Validation

- must run before review
- must record structured results
- must block advancement if required checks fail

### Review

- must operate on validated output
- must record structured results
- may trigger local revision, pause, or fail behavior depending on policy

### Testing

- must operate after review in the default built-in order
- must record structured results
- must gate docs/finalization unless policy explicitly allows override

---

## 16. Documentation and provenance lifecycle

After the main quality gates succeed:

1. provenance is refreshed
2. documentation views are built
3. the node is finalized

This order is the default because:

- provenance updates feed docs
- docs should reflect the final validated/reviewed/tested node state

If a project needs different behavior, the deviation must be explicit in policy and compiled workflow lineage.

---

## 17. Regeneration transitions

When a node or its specification changes:

1. create a new node version
2. compile a new immutable workflow snapshot
3. regenerate affected descendants if required
4. rebuild the node from seed
5. rebuild ancestors from seed to the top node
6. only after stable rebuild should the new lineage supersede the old lineage

Key rule:

- supersession should not cut over early if the rebuilt lineage is not yet stable

---

## 18. Rectification lifecycle

Rectification is a structured rebuild process centered on seed commits and current child finals.

For a node under rectification:

1. transition to `RECTIFYING_SELF`
2. reset to seed
3. merge current child finals in deterministic order
4. reconcile node-local output
5. run validation
6. run review
7. run testing
8. refresh provenance
9. build docs
10. finalize node
11. if successful, continue upstream rectification if required

For ancestors:

1. transition to `RECTIFYING_UPSTREAM`
2. repeat the same rebuild-from-seed logic using current child finals

Implementation staging note:

- the current implementation now supports the durable child-result collection part of rectification and the parent-local reconcile handoff
- parent nodes can inspect authoritative child finals, blocked children, and deterministic merge order
- parent merge execution now shells out to live git fetch/merge across the per-version runtime repos, records durable `merge_events` and `merge_conflicts`, and writes the reconcile context into the active run cursor
- finalize execution now creates a real finalize commit and records the resulting `final_commit_sha`

---

## 19. Supersession and cutover rule

When a new node version is created:

- the old version remains historical truth for any already-completed lineage
- the new version becomes authoritative only after its required rebuild path is stable enough for cutover

At minimum, cutover policy must define:

- whether child descendants must finish first
- whether ancestor rectification must finish first
- what happens to active runs on older versions

Recommended default:

- cut over only after the new node version and required upstream lineage are stable

During rebuild, the new lineage should be treated as a durable candidate lineage that is queryable but not yet authoritative.

Until cutover occurs:

- the prior authoritative lineage remains the current effective version for dependency evaluation and default operator views
- candidate versions remain inspectable through lineage and history views
- old active runs must not be silently discarded or hidden

---

## 20. Required introspection surfaces

Operators and AI sessions must be able to inspect:

- node lifecycle state
- active run state
- compiled workflow
- current task pointer
- current subtask pointer
- subtask attempt history
- dependency blockers
- pause flags and gating points
- validation/review/testing results
- session binding
- seed/final commits
- merge and rebuild history
- latest summaries

No critical lifecycle variable should be hidden only in memory.

---

## 21. V2 closure notes

This V2 lifecycle spec resolves or reduces the following prior gaps:

- canonical quality-gate ordering
- stronger pause and escalation semantics
- stronger alignment with explicit review/testing/docs families
- clearer supersession cutover expectations

Remaining follow-on work still needed:

- fold hybrid manual-vs-layout child-set rules into implementation-facing hierarchy metadata
- finalize active-old-run handling during supersession
Implementation note: subtree regeneration and upstream rectification now create durable candidate lineages plus `rebuild_events`; candidate cutover is blocked until the rebuild path marks the candidate stable. The runtime now also exposes explicit rebuild-coordination and cutover-readiness reads so active-run and active-session conflicts are inspectable before mutation.
Implementation note: the current default compiled workflow now includes `validate_node` as a durable gate after execution, and `workflow advance` enforces required validation success before the run can continue or complete.
Implementation note: user-gated pauses are now persisted through both `node_run_state.execution_cursor_json.pause_context` and the narrow `workflow_events` history. `pause_entered`, `pause_cleared`, and `pause_resumed` are emitted durably, `node pause-state` reads the mirrored lifecycle row, and resume is blocked until the active pause flag is approved unless the daemon is performing a forced recovery action.
## Implementation Note: Compile Variants

- authoritative compile remains the default path used for current lifecycle admission
- candidate versions can now be compiled explicitly as first-class operator targets
- rebuild-created candidate versions can also be compiled explicitly and are surfaced as `rebuild_candidate` compile variants
- compile variant is inspectable from compiled workflow and compile-failure payloads through frozen `compile_context` metadata
- this phase does not change cutover rules by itself; rebuild-stability and merge-conflict gates still control candidate promotion

## Implementation Note: Scheduling Explanation

- the current child-scheduling slice still does not auto-start children
- it now does expose richer scheduling explanation derived from current lifecycle, run, pause, and dependency state
- blocked children can now explain whether they are:
  - waiting on dependencies
  - paused behind a gate
  - already running
  - not compiled or otherwise not ready
