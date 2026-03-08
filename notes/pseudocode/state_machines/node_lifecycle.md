# State Machine: Node Lifecycle

## Purpose

Normalize the core node lifecycle vocabulary and the allowed high-level transitions so pseudocode modules use one bounded model instead of slightly different state assumptions.

---

## Source notes

Primary:

- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/catalogs/vocabulary/state_value_catalog.md`

Supporting:

- `notes/contracts/persistence/compile_failure_persistence.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/contracts/parent_child/parent_failure_decision_spec.md`

---

## Canonical state set

Use this state set for first-pass pseudocode:

- `DRAFT`
- `COMPILE_FAILED`
- `COMPILED`
- `READY`
- `RUNNING`
- `WAITING_ON_CHILDREN`
- `WAITING_ON_SIBLING_DEPENDENCY`
- `VALIDATION_PENDING`
- `REVIEW_PENDING`
- `TESTING_PENDING`
- `RECTIFYING_SELF`
- `RECTIFYING_UPSTREAM`
- `PAUSED_FOR_USER`
- `FAILED_TO_PARENT`
- `COMPLETE`
- `SUPERSEDED`
- `CANCELLED`

This list is intentionally aligned with [state_value_catalog.md](/mnt/c/Users/Nathan/Documents/GitHub/ai_coding_site_v2/notes/catalogs/vocabulary/state_value_catalog.md).

---

## State meanings

- `DRAFT`: node version exists but no authoritative compiled workflow is ready
- `COMPILE_FAILED`: latest compile attempt failed and the node is not runnable
- `COMPILED`: compiled workflow exists but readiness/admission still depends on other checks
- `READY`: node version is runnable and may be admitted
- `RUNNING`: an active node run currently owns execution
- `WAITING_ON_CHILDREN`: parent cannot continue until required children resolve
- `WAITING_ON_SIBLING_DEPENDENCY`: node cannot start or continue until required sibling dependency resolves
- `VALIDATION_PENDING`: semantic stage marker before required validations complete
- `REVIEW_PENDING`: semantic stage marker before required review completes
- `TESTING_PENDING`: semantic stage marker before required tests complete
- `RECTIFYING_SELF`: node is reconciling its own branch/state from seed or conflict
- `RECTIFYING_UPSTREAM`: node is participating in upstream rectification/rebuild
- `PAUSED_FOR_USER`: autonomous progress is intentionally stopped pending user or operator action
- `FAILED_TO_PARENT`: node failed and escalated to its parent
- `COMPLETE`: node finished its required execution and finalization path
- `SUPERSEDED`: a newer authoritative version replaced this node version
- `CANCELLED`: execution or lineage was intentionally terminated

---

## Core transitions

### Creation and compile path

- `DRAFT -> COMPILED`
  Condition: compile succeeds and compiled workflow is persisted

- `DRAFT -> COMPILE_FAILED`
  Condition: compile fails before a runnable workflow exists

- `COMPILE_FAILED -> COMPILED`
  Condition: recompile succeeds

- `COMPILED -> READY`
  Condition: node version is marked runnable and eligible for admission

### Admission and execution path

- `READY -> RUNNING`
  Condition: run is admitted and authoritative execution starts

- `RUNNING -> WAITING_ON_CHILDREN`
  Condition: current parent stage requires child completion

- `RUNNING -> WAITING_ON_SIBLING_DEPENDENCY`
  Condition: current stage is blocked on a required sibling dependency

- `WAITING_ON_CHILDREN -> RUNNING`
  Condition: required children become satisfied

- `WAITING_ON_SIBLING_DEPENDENCY -> RUNNING`
  Condition: required sibling dependency becomes satisfied

### Quality-gate stage markers

- `RUNNING -> VALIDATION_PENDING`
- `VALIDATION_PENDING -> REVIEW_PENDING`
- `REVIEW_PENDING -> TESTING_PENDING`
- `TESTING_PENDING -> RUNNING`

Use these as semantic visible stages only where the implementation chooses to surface them as node lifecycle states rather than purely subtask/run-state detail.

### Pause and failure path

- `RUNNING -> PAUSED_FOR_USER`
- `WAITING_ON_CHILDREN -> PAUSED_FOR_USER`
- `WAITING_ON_SIBLING_DEPENDENCY -> PAUSED_FOR_USER`
  Condition: user gate, ambiguity, safety threshold, or recovery ambiguity

- `PAUSED_FOR_USER -> RUNNING`
  Condition: pause flag cleared and same compiled workflow/cursor resume is valid

- `RUNNING -> FAILED_TO_PARENT`
  Condition: subtask or child failure exhausts local recovery and escalates

### Rectification and rebuild path

- `RUNNING -> RECTIFYING_SELF`
- `RUNNING -> RECTIFYING_UPSTREAM`
- `PAUSED_FOR_USER -> RECTIFYING_SELF`
- `PAUSED_FOR_USER -> RECTIFYING_UPSTREAM`
  Condition: rectification or rebuild path is explicitly entered

### Terminal path

- `RUNNING -> COMPLETE`
  Condition: all required stages and finalization succeed

- `COMPLETE -> SUPERSEDED`
- `FAILED_TO_PARENT -> SUPERSEDED`
- `COMPILE_FAILED -> SUPERSEDED`
  Condition: newer authoritative node version replaces this version

- `DRAFT -> CANCELLED`
- `READY -> CANCELLED`
- `RUNNING -> CANCELLED`
- `PAUSED_FOR_USER -> CANCELLED`
  Condition: explicit cancellation

---

## Transition guards

- no run admission from `DRAFT` or `COMPILE_FAILED`
- no automatic resume from `PAUSED_FOR_USER` without clearing the pause cause
- no silent transition from `hybrid` tree authority conflict to structural mutation
- no waiting state when the blocker set is impossible to satisfy
- no transition out of `SUPERSEDED` back into active execution

---

## Interaction with run status

Node lifecycle state and run status are related but distinct.

Recommended run statuses:

- `PENDING`
- `RUNNING`
- `PAUSED`
- `FAILED`
- `COMPLETE`
- `CANCELLED`

Examples:

- node may be `READY` while there is no active run yet
- node may be `PAUSED_FOR_USER` while run status is `PAUSED`
- node may be `FAILED_TO_PARENT` while the latest run status is `FAILED`

---

## Illegal or suspicious transitions

- `COMPILE_FAILED -> RUNNING`
- `DRAFT -> RUNNING`
- `SUPERSEDED -> RUNNING`
- `FAILED_TO_PARENT -> RUNNING` without explicit retry/regeneration path
- `WAITING_ON_CHILDREN -> COMPLETE` while required children are incomplete

These should be treated as invariant violations or require a dedicated exceptional path.

---

## Pseudotests

### `failed_compile_cannot_be_admitted`

Given:

- node lifecycle state is `COMPILE_FAILED`

Expect:

- admission is rejected

### `paused_node_resumes_only_after_pause_cleared`

Given:

- node lifecycle state is `PAUSED_FOR_USER`

Expect:

- state does not return to `RUNNING` automatically

### `superseded_node_cannot_restart_execution`

Given:

- node lifecycle state is `SUPERSEDED`

Expect:

- no active run can be admitted for that node version
