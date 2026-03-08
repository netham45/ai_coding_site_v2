# Pause And Workflow Event Persistence

## Purpose

This document defines when the system should persist explicit pause and workflow events instead of relying only on current state plus summaries.

The current design already has:

- current lifecycle state
- run state
- summaries
- session events
- subtask attempt history

The remaining question is whether those are enough, or whether some orchestration transitions deserve a dedicated event-history model.

Related documents:

- `notes/database_schema_spec_v2.md`
- `notes/node_lifecycle_spec_v2.md`
- `notes/runtime_command_loop_spec_v2.md`
- `notes/auditability_checklist.md`
- `notes/cross_spec_gap_matrix.md`

---

## Core Decision

The system should record dedicated workflow events for pause, recovery, parent-decision, and cutover history.

The design should still be selective:

- not every subtask transition needs a workflow event
- major orchestration transitions should have canonical event history

---

## Recommended Rule

Persist explicit events when the transition is operationally meaningful and not easily reconstructible from current state plus attempts.

Recommended event-worthy cases:

- pause entered
- pause cleared or resumed
- run recovery decision
- replacement session created
- authoritative cutover completed
- workflow-level failure escalation decisions

Less necessary as dedicated events:

- ordinary subtask completion, because subtask attempts already cover that well

---

## Why Current State Alone Is Not Always Enough

Current state can show:

- where the node is now

But it often cannot show:

- how many times the node paused
- why the node previously paused and resumed
- what recovery path was chosen
- when the parent switched from retry to replan
- when authoritative cutover happened

That history can matter a lot for:

- debugging
- auditability
- operator trust

---

## Event Categories Worth Tracking

Recommended workflow-event categories:

### E01. Pause events

Examples:

- entered pause
- resumed from pause
- pause cleared by approval

### E02. Recovery events

Examples:

- session recovery attempted
- existing session resumed
- replacement session created
- recovery failed

### E03. Parent decision events

Examples:

- retry child chosen
- regenerate child chosen
- parent replan chosen
- pause for user chosen

### E04. Cutover events

Examples:

- candidate lineage marked authoritative
- replaced lineage marked superseded

### E05. Compile failure events

If compile failures get a dedicated table, they may not need to also be generic workflow events.

Recommended current stance:

- compile failures can stay in their own dedicated structure

---

## Minimal Event Model

If the system wants a bounded first implementation, use a minimal event table focused on the categories above.

Suggested conceptual table:

- `workflow_events`

Possible fields:

- `id`
- `node_version_id`
- `node_run_id`
- `event_type`
- `event_scope`
- `payload_json`
- `created_at`

Where:

- `event_type` captures what happened
- `event_scope` distinguishes categories such as pause, recovery, parent_decision, cutover

---

## Event Type Candidates

Recommended workflow event types:

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

This list can be adjusted, but the categories should remain bounded and intentional.

---

## Event Payload Guidance

The payload should be structured enough to answer:

- why the event happened
- what object(s) it affected
- what decision was made
- what the next expected state became

Examples:

### Pause event payload

- pause flag
- summary ID
- triggering subtask ID

### Recovery event payload

- old session ID
- new session ID if replacement occurred
- recovery reason

### Parent decision event payload

- failed child ID
- failure class
- decision type
- relevant counters

### Cutover event payload

- old authoritative version ID
- new authoritative version ID
- scope of cutover

---

## What Should Still Use Existing Structures

Not everything needs workflow events.

Keep using:

- `subtask_attempts` for ordinary execution attempts
- `session_events` for low-level session activity
- `summaries` for human-readable summaries
- dedicated result tables for validation/review/testing

The workflow event model should fill gaps those structures do not already cover well.

---

## Recommended First-Implementation Stance

Recommended bounded first implementation:

1. use a small canonical `workflow_events` table
2. use it only for:
   - pause events
   - recovery events
   - parent decision events
   - cutover events
3. do not mirror every subtask event into it

This gives meaningful orchestration history without turning the system into an event-sourcing project.

---

## If You Do Not Add Workflow Events Yet

If first implementation wants to stay simpler in surrounding systems:

- rely on `summaries`
- rely on `session_events`
- rely on `subtask_attempts`
- rely on current `node_run_state`

But accept the tradeoff:

- some orchestration history will be harder to reconstruct cleanly
- but the canonical database model should still retain workflow-event storage

Recommended stance:

- add workflow events if you can
- but keep the scope narrow and high-value

---

## Pseudocode

```python
def record_pause_event(node_run_id, pause_flag, summary_id):
    create_workflow_event(
        node_run_id=node_run_id,
        event_type="pause_entered",
        event_scope="pause",
        payload={
            "pause_flag": pause_flag,
            "summary_id": summary_id,
        },
    )


def record_parent_decision_event(parent_node_id, child_node_id, decision_type, failure_class):
    create_workflow_event(
        node_version_id=parent_node_id,
        event_type=decision_type,
        event_scope="parent_decision",
        payload={
            "child_node_id": child_node_id,
            "failure_class": failure_class,
        },
    )
```

---

## DB Implications

Recommended addition:

- `workflow_events`

Potential indexes:

- `(node_version_id)`
- `(node_run_id)`
- `(event_type)`
- `(event_scope)`
- `(created_at)`

This table should remain small and intentional, not a dumping ground for every possible runtime action.

---

## CLI Implications

Useful CLI capabilities if workflow events exist:

- `ai-tool workflow events --node <id>`
- `ai-tool workflow events --run <id>`
- `ai-tool node pause-state --node <id>`

Potential useful additions:

- `ai-tool node decision-history --node <id>`
- `ai-tool node recovery-history --node <id>`

If names differ, the capability should still exist.

---

## Auditability Implications

Workflow events would significantly improve the system’s ability to answer:

- how many times was this node paused
- why did it resume
- when did recovery happen
- what parent failure decisions were made
- when did authoritative cutover occur

These are all hard to answer cleanly from current state alone.

---

## Open Decisions Still Remaining

### D01. Dedicated table in first implementation

Recommended direction:

- yes, but keep it narrow

### D02. Whether pause and resume are both events

Recommended direction:

- yes, because paired transitions are useful operationally

### D03. Whether compile-failure belongs here

Recommended direction:

- no, prefer a dedicated compile-failure structure

---

## Recommended Next Follow-On Work

The next docs that should absorb this logic are:

1. `notes/database_schema_spec_v2.md`
2. `notes/runtime_command_loop_spec_v2.md`
3. `notes/cli_surface_spec_v2.md`
4. `notes/cross_spec_gap_matrix.md`

Then reduce the severity of the pause/workflow-event gap.

---

## Exit Criteria

This note is complete enough when:

- event-worthy orchestration transitions are explicit
- the narrow event scope is explicit
- DB and CLI implications are identified

At that point, the system has a concrete answer to whether current state alone is enough.
