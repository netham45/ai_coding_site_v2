# Runtime Pseudocode Plan

## Purpose

This document defines the pseudocode planning surface for the orchestration runtime.

The goal is to make the operational logic explicit enough that:

- missing YAML artifacts become obvious
- missing database state becomes obvious
- missing CLI semantics become obvious
- missing failure and recovery behavior becomes obvious
- contradictions between specs can be identified before implementation

This is not the final runtime spec. It is the planning document for the pseudocode package that should feed into `notes/runtime_command_loop_spec_v2.md` and related v2 specs.

Related documents:

- `notes/runtime_command_loop_spec.md`
- `notes/node_lifecycle_spec_revised.md`
- `notes/git_rectification_spec_revised.md`
- `notes/database_schema_v2_expansion.md`
- `notes/default_yaml_library_plan.md`

---

## Goals

The runtime pseudocode package should answer:

- how nodes are created
- how workflows are compiled
- how runs are admitted
- how sessions are bound and resumed
- how tasks and subtasks execute
- how validations, reviews, and testing run
- how child nodes and child sessions are handled
- how pause gates and failures are handled
- how regeneration and rectification work
- how docs and provenance are refreshed

---

## Pseudocode Design Rules

### Rule 1: Every important durable state change should be explicit

If runtime behavior changes node state, run state, session state, or lineage state, that change should appear explicitly in the pseudocode.

### Rule 2: Happy path is not enough

Every major pseudocode module should consider:

- success path
- validation failure path
- runtime failure path
- pause-for-user path
- recovery/resume path where relevant

### Rule 3: Runtime behavior should be CLI-compatible

The pseudocode should align with the principle that AI sessions operate through CLI-visible interactions rather than hidden in-memory control flow.

### Rule 4: Parent-child ownership should be clear

The pseudocode should make it obvious when ownership belongs to:

- the node
- the node run
- the primary session
- a pushed child session
- a parent node

### Rule 5: Compilation and execution boundaries should stay clean

Compilation resolves mutable YAML into immutable workflow artifacts.
Execution runs compiled workflow instances.
The pseudocode should not blur those boundaries.

---

## Runtime Module Inventory

The following runtime modules should be written in pseudocode form.

### R01. Node creation and version initialization

- `create_top_level_node(...)`
- `create_child_node(...)`
- `create_superseding_node_version(...)`

### R02. Source loading and workflow compilation

- `load_source_documents(...)`
- `resolve_overrides(...)`
- `expand_hooks(...)`
- `validate_source_yaml(...)`
- `compile_workflow(...)`
- `persist_compiled_workflow(...)`

### R03. Run admission and preparation

- `admit_node_run(...)`
- `check_node_dependency_readiness(...)`
- `create_node_run(...)`
- `initialize_run_cursor(...)`

### R04. Session lifecycle

- `bind_primary_session(...)`
- `resume_or_rebind_session(...)`
- `record_session_heartbeat(...)`
- `attach_to_tmux_session(...)`

### R05. Canonical execution loop

- `run_node_loop(...)`
- `get_current_subtask(...)`
- `execute_compiled_subtask(...)`
- `advance_cursor(...)`

### R06. Subtask type handlers

- `execute_run_prompt_subtask(...)`
- `execute_run_command_subtask(...)`
- `execute_build_context_subtask(...)`
- `execute_wait_for_children_subtask(...)`
- `execute_wait_for_sibling_dependency_subtask(...)`
- `execute_validate_subtask(...)`
- `execute_review_subtask(...)`
- `execute_build_docs_subtask(...)`
- `execute_write_summary_subtask(...)`
- `execute_finalize_node_subtask(...)`
- `execute_spawn_child_session_subtask(...)`
- `execute_spawn_child_node_subtask(...)`
- `execute_reset_to_seed_subtask(...)`
- `execute_merge_children_subtask(...)`

### R07. Quality gates

- `run_validation_checks(...)`
- `run_review_stage(...)`
- `run_testing_stage(...)`

### R08. Pause and failure behavior

- `pause_for_user(...)`
- `record_failure_summary(...)`
- `handle_subtask_failure(...)`
- `handle_child_failure_at_parent(...)`

### R09. Child node orchestration

- `materialize_layout_children(...)`
- `schedule_ready_children(...)`
- `wait_for_child_completion(...)`
- `collect_child_results(...)`

### R10. Pushed child session orchestration

- `push_child_session(...)`
- `run_child_session_work(...)`
- `pop_child_session(...)`

### R11. Recovery and nudge behavior

- `recover_interrupted_run(...)`
- `detect_idle_session(...)`
- `nudge_idle_session(...)`
- `recover_cursor_state(...)`

### R12. Rebuild and rectification

- `regenerate_node_and_descendants(...)`
- `rectify_node_from_seed(...)`
- `rectify_upstream(...)`
- `handle_merge_conflict(...)`

### R13. Support systems

- `build_docs_for_node(...)`
- `update_provenance_for_node(...)`
- `register_prompt_history(...)`
- `register_summary(...)`

---

## Canonical Flow Inventory

The runtime pseudocode should explicitly cover these end-to-end flows.

## Flow A: Create and compile a new top-level node

1. create logical node identity
2. create first node version
3. load source YAML
4. resolve overrides
5. validate YAML
6. expand hooks
7. compile immutable workflow
8. persist compiled workflow and sources
9. mark node ready

## Flow B: Admit and run a ready node

1. verify dependencies are satisfied
2. create node run
3. initialize run cursor
4. bind or create session
5. enter subtask loop
6. finalize node if loop completes

## Flow C: Execute one compiled subtask

1. load subtask definition from compiled workflow
2. mark subtask start
3. execute handler
4. register outputs
5. run validations
6. record attempt result
7. advance or fail

## Flow D: Spawn and reconcile children

1. load layout
2. create child nodes
3. create child dependencies
4. schedule ready children
5. wait for blocked children
6. collect child summaries and finals
7. reconcile parent

## Flow E: Pause or fail

1. detect gating or failure condition
2. register summary
3. update run state
4. update node lifecycle state
5. either await user or fail to parent

## Flow F: Recover interrupted work

1. inspect current node/run/session state
2. recover existing session if possible
3. otherwise create replacement session
4. reload compiled workflow and cursor
5. continue current subtask

## Flow G: Rectify after change

1. create superseding node version
2. recompile workflow
3. regenerate descendants if needed
4. rectify changed node from seed
5. rectify ancestors upward
6. cut over only after stable rebuild

---

## Pseudocode Modules

The following sections define the initial module list and what each module must answer.

## R01. `create_top_level_node(...)`

### Purpose

Create a new top-level node, its initial version, and its first compiled workflow.

### Must define

- required inputs
- branch initialization behavior
- source YAML selection
- compilation call sequence
- failure path if compilation fails

### Questions it must answer

- when is the node considered created versus merely drafted
- whether branch creation happens before or after successful compilation

---

## R02. `create_child_node(...)`

### Purpose

Create a child node from a parent layout entry.

### Must define

- parent-child linkage persistence
- dependency creation
- inherited context or summaries
- branch naming and seed initialization

### Questions it must answer

- when child creation should fail because layout data is invalid
- how much parent context is passed structurally versus fetched later

---

## R03. `create_superseding_node_version(...)`

### Purpose

Create a new version of an existing logical node for regeneration or rectification.

### Must define

- old/new version linkage
- copied metadata versus regenerated metadata
- branch generation behavior
- active-version cutover timing

### Questions it must answer

- whether descendants are superseded eagerly or lazily
- how active runs on old versions are handled

---

## R04. `load_source_documents(...)`

### Purpose

Load the built-in and project-local YAML inputs needed for a node compilation.

### Must define

- source discovery order
- document family identification
- source-role labeling
- hash capture

### Questions it must answer

- how built-in and project-local duplicates are identified
- how missing source files are treated

---

## R05. `resolve_overrides(...)`

### Purpose

Apply project-local overrides and merge logic to produce resolved YAML inputs.

### Must define

- override precedence
- merge behavior by document family
- conflict detection behavior
- source lineage recording

### Questions it must answer

- whether override conflicts are fatal
- whether some fields replace while others merge

---

## R06. `validate_source_yaml(...)`

### Purpose

Validate resolved YAML against the appropriate schema families before compilation.

### Must define

- schema selection
- validation error reporting
- failure handling

### Questions it must answer

- whether warnings exist or only hard errors
- how cross-document validation is handled

---

## R07. `expand_hooks(...)`

### Purpose

Insert hook-driven stages into the resolved workflow before compilation finalization.

### Must define

- hook selection rules
- ordering rules
- conflict rules
- inserted subtask metadata

### Questions it must answer

- how multiple hooks at the same insertion point compose
- whether hook expansions can themselves trigger validation or review additions

---

## R08. `compile_workflow(...)`

### Purpose

Produce the immutable compiled workflow snapshot used for execution.

### Must define

- task ordering
- subtask ordering
- dependency expansion
- durable compiled IDs
- resolved prompt/command freezing

### Questions it must answer

- how reusable subtask templates become compiled instances
- how source references are preserved per compiled item

---

## R09. `admit_node_run(...)`

### Purpose

Determine whether a node is eligible to start a run.

### Must define

- dependency-readiness checks
- current lifecycle-state checks
- conflicting active-run checks
- pause-gate checks

### Questions it must answer

- how queued-but-not-ready nodes are represented
- whether admission can pre-create runs for blocked nodes

---

## R10. `bind_primary_session(...)`

### Purpose

Bind the current execution to a primary session.

### Must define

- session creation versus reuse
- tmux binding
- provider session identity capture
- current run linkage

### Questions it must answer

- what minimum state is required before a session can execute work
- when session recovery is attempted instead of new-session creation

---

## R11. `run_node_loop(...)`

### Purpose

Define the canonical loop that repeatedly executes compiled subtasks until completion, pause, or failure.

### Must define

- cursor lookup
- subtask dispatch
- summary registration
- completion/failure branching
- finalization transition

### Questions it must answer

- whether loop orchestration lives inside the session or a supervising runtime
- how often state is flushed durably

---

## R12. `execute_compiled_subtask(...)`

### Purpose

Dispatch a compiled subtask instance to the correct runtime handler.

### Must define

- subtask attempt creation
- handler selection
- output collection
- validation integration
- result persistence

### Questions it must answer

- whether validations run inside or after handler execution
- how structured versus free-form outputs are normalized

---

## R13. `run_validation_checks(...)`

### Purpose

Evaluate the required checks for a subtask or node stage.

### Must define

- check execution order
- pass/fail recording
- summary generation
- gate behavior on failure

### Questions it must answer

- whether all checks run or fail-fast is allowed
- how command-based and schema-based checks return structured results

---

## R14. `run_review_stage(...)`

### Purpose

Perform review against requirements, acceptance criteria, and policy.

### Must define

- review input construction
- review output persistence
- pass/fail/revise behavior

### Questions it must answer

- whether review can trigger local revision automatically
- how review summaries are linked to the node/run

---

## R15. `run_testing_stage(...)`

### Purpose

Execute testing gates configured for a node.

### Must define

- test suite discovery
- execution order
- retry policy
- failure summary capture

### Questions it must answer

- whether tests are modeled as validations, reviews, or their own result type
- how flaky or retried tests are persisted

---

## R16. `pause_for_user(...)`

### Purpose

Pause execution at a user-gated boundary while preserving enough context to resume cleanly.

### Must define

- pause reason capture
- summary registration
- lifecycle-state updates
- resume preconditions

### Questions it must answer

- how multiple pending gate reasons are represented
- whether a pause is tied to the next subtask or current subtask completion

---

## R17. `handle_subtask_failure(...)`

### Purpose

Handle a failed subtask according to retry and escalation policy.

### Must define

- retry eligibility
- failure summary registration
- lifecycle-state updates
- fail-to-parent behavior

### Questions it must answer

- whether some failure classes bypass retries
- how partial outputs are retained

---

## R18. `handle_child_failure_at_parent(...)`

### Purpose

Decide what a parent does when a child node fails.

### Must define

- threshold tracking
- child-failure summary aggregation
- retry/replan/defer decisions
- user-facing escalation summary

### Questions it must answer

- whether the parent can selectively regenerate a child versus replanning the layer
- how consecutive versus total failures change behavior

---

## R19. `materialize_layout_children(...)`

### Purpose

Create all children defined by a layout and persist their relationships and dependencies.

### Must define

- layout validation
- child creation ordering
- dependency creation
- idempotency behavior

### Questions it must answer

- whether child materialization can be resumed safely
- how duplicate or stale layout entries are handled

---

## R20. `schedule_ready_children(...)`

### Purpose

Start any child nodes whose dependencies are currently satisfied.

### Must define

- readiness calculation
- concurrent scheduling behavior
- blocked-child tracking

### Questions it must answer

- whether scheduling is push-based or polling-based
- how scheduler fairness or prioritization works

---

## R21. `push_child_session(...)`

### Purpose

Launch a bounded child session for context-isolated work.

### Must define

- parent session linkage
- context snapshot
- allowed scope of work
- return-summary requirements

### Questions it must answer

- who owns timeout and cleanup
- how child-session artifacts re-enter parent context

---

## R22. `recover_interrupted_run(...)`

### Purpose

Recover a node run after session loss, tmux loss, host restart, or similar interruption.

### Must define

- state inspection order
- recover-vs-replace session decision
- cursor restoration
- resumability checks

### Questions it must answer

- when a run is non-resumable
- how mismatched session and git state are resolved

---

## R23. `nudge_idle_session(...)`

### Purpose

Reissue current work context when a session becomes idle unexpectedly.

### Must define

- idle detection thresholds
- nudge payload contents
- repeated nudge behavior
- escalation after repeated idleness

### Questions it must answer

- when a nudge becomes a failure or user-defer event
- whether nudges should reset any timers or counters

---

## R24. `regenerate_node_and_descendants(...)`

### Purpose

Create new versions for a changed subtree and rerun it.

### Must define

- supersession order
- descendant regeneration policy
- workflow recompilation policy
- cutover rules

### Questions it must answer

- whether unchanged descendants can ever be reused
- how concurrent rebuilds are serialized

---

## R25. `rectify_node_from_seed(...)`

### Purpose

Rebuild a node by resetting to seed, merging current child finals, and rerunning node-local work.

### Must define

- reset behavior
- merge order
- reconcile stage
- validation/review/testing/docs/provenance ordering
- final commit registration

### Questions it must answer

- whether provenance refresh happens before or after docs
- how unresolved conflicts are persisted and surfaced

---

## R26. `rectify_upstream(...)`

### Purpose

Walk from a changed node upward to the top node, rebuilding each ancestor from seed.

### Must define

- ancestor traversal
- sibling reuse behavior
- failure propagation
- user-gated merge-to-base logic

### Questions it must answer

- when the old lineage becomes superseded
- whether partial upstream success is allowed

---

## R27. `build_docs_for_node(...)`

### Purpose

Build local or merged documentation views for a node.

### Must define

- docs input sources
- local versus merged view behavior
- persistence behavior
- rebuild triggers

### Questions it must answer

- how docs differ between node-local and merged-tree scopes
- whether docs are rebuilt every finalization or only on relevant changes

---

## R28. `update_provenance_for_node(...)`

### Purpose

Refresh code entities, relations, and rationale links after node-local work or rebuild.

### Must define

- extraction sources
- change detection
- relation updates
- rationale attachment logic

### Questions it must answer

- how stable entity identity is maintained across refactors
- whether provenance runs before or after docs generation

---

## Quality-Gate Ordering Candidates

One of the biggest unresolved runtime questions is the canonical ordering of validation, review, testing, docs, provenance, and finalize.

The current likely candidates are:

### Candidate A

1. reconcile
2. validation
3. review
4. testing
5. docs
6. provenance
7. finalize

### Candidate B

1. reconcile
2. validation
3. testing
4. review
5. docs
6. provenance
7. finalize

### Candidate C

1. reconcile
2. validation
3. review
4. testing
5. provenance
6. docs
7. finalize

This ordering should be frozen during the v2 rewrite stage.

---

## Highest-Priority Pseudocode Gaps

Based on current specs, these are the highest-priority logic gaps:

1. parent-side failure decision algorithm
2. hook expansion and ordering algorithm
3. child materialization and scheduling algorithm
4. session recovery decision tree
5. idle-detection escalation logic
6. review/testing result handling and persistence rules
7. cutover semantics during supersession and upstream rebuild

---

## Recommended Follow-On Documents

After this pseudocode planning document, the next highest-value docs are:

- `notes/cross_spec_gap_matrix.md`
- `notes/action_automation_matrix.md`
- `notes/auditability_checklist.md`

Those will use this pseudocode plan to expose inconsistencies and unresolved ownership rules.

---

## Exit Criteria

This runtime pseudocode planning phase should be considered complete when:

- all major runtime modules are enumerated
- each module has a clear purpose and unresolved-question list
- the core end-to-end flows are captured
- the highest-priority logic gaps are explicit
- the runtime is concrete enough to drive the cross-spec review

At that point, the system is ready for a dedicated contradiction and gap pass across YAML, DB, CLI, runtime, and git behavior.
