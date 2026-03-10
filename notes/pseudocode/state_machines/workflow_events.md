# State Machine: Workflow Events

## Purpose

Normalize the bounded event history for orchestration-level transitions that are not well represented by current state alone.

This is intentionally narrow. It is not a full event-sourcing model.

---

## Source notes

Primary:

- `notes/contracts/persistence/pause_workflow_event_persistence.md`
- `notes/specs/cli/cli_surface_spec_v2.md`

Supporting:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/catalogs/audit/auditability_checklist.md`
- `notes/catalogs/vocabulary/state_value_catalog.md`

---

## Canonical event scopes

- `pause`
- `recovery`
- `parent_decision`
- `cutover`
- `run`

---

## Canonical event types

Use this bounded first-pass set:

- `run_admitted`
- `pause_entered`
- `pause_cleared`
- `pause_resumed`
- `recovery_attempted`
- `recovery_succeeded`
- `replacement_session_created`
- `recovery_failed`
- `parent_retry_child`
- `parent_regenerate_child`
- `parent_replan`
- `parent_pause_for_user`
- `cutover_completed`
- `lineage_superseded`

Compile failures remain in dedicated compile-failure history, not generic workflow events.

---

## Event-worthiness rule

Persist a workflow event when the transition is:

- operationally meaningful
- not fully reconstructible from ordinary subtask attempts alone
- important for auditability or operator trust

Do not emit workflow events for ordinary subtask completion when subtask-attempt history already covers that well.

---

## Event payload minimums

Every workflow event should preserve enough structure to answer:

- why it happened
- what object it affected
- what decision or transition occurred
- what next state became active

---

## Core transitions

### Pause scope

- enter pause
- clear pause
- resume from pause

Implementation note:

- the current implementation records `pause_entered` when a manual pause, idle escalation, or gated compiled subtask pushes the run into `PAUSED_FOR_USER`
- explicit approval records `pause_cleared` while leaving the run paused
- successful resume records `pause_resumed`

### Recovery scope

- record recovery attempt
- record success or failure
- record replacement-session creation when applicable

### Parent decision scope

- retry child
- regenerate child
- replan parent
- pause for user

### Cutover scope

- candidate scope marked authoritative
- replaced scope marked superseded

### Run scope

- run admitted

---

## Transition guards

- no duplicate event should be emitted for the same single transition if one durable action already claims it
- workflow events complement state tables and summaries; they do not replace them
- event emission should happen transactionally with the authoritative transition where feasible

---

## CLI-visible expectations

`ai-tool node events --node <id>` or equivalent should expose at minimum:

- pause events
- recovery events
- parent decision events
- cutover events
- run admission events

---

## Pseudotests

### `records_pause_event_when_user_gate_enters_pause`

Given:

- runtime transitions into `PAUSED_FOR_USER`

Expect:

- `pause_entered` event is emitted

### `records_recovery_attempt_and_outcome`

Given:

- interrupted run recovery is evaluated

Expect:

- `recovery_attempted` and terminal recovery event are emitted

### `records_cutover_and_supersession_separately`

Given:

- candidate lineage becomes authoritative

Expect:

- `cutover_completed` and `lineage_superseded` history are both available
