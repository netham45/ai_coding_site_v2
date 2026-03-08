# Flow 13: Human Gate And Intervention

## Purpose

Support the cases where automation must stop and ask a human to approve, reject, choose a reconciliation path, or provide additional direction.

## Covers journeys

- active pause gate inspection
- merge approval
- hybrid-tree reconciliation choice
- unsafe recovery or cutover decision
- retry exhaustion requiring human input

## Entry conditions

- runtime policy or a failure state requires human intervention before continuing

## Task flow

1. create a gate or intervention record with explicit reason
2. persist the current state snapshot and required decision options
3. expose gate status through CLI and UI surfaces
4. accept a human decision, note, or updated artifact
5. validate that the decision is legal for the current state
6. apply the chosen branch: approve, reject, defer, modify, or replan
7. resume or keep paused accordingly

## Required subtasks

- `create_gate_record`
- `persist_gate_context_snapshot`
- `publish_gate_state`
- `accept_human_decision`
- `validate_decision_legality`
- `apply_decision`
- `resume_or_hold`

## Required capabilities

- `ai-tool node pause-state ...`
- merge approval surfaces
- reconciliation decision surfaces
- user gating and pause-event persistence
- clear resume semantics after intervention

## Durable outputs

- gate records
- intervention summaries
- human decision history
- resumed or continued pause state

## Failure cases that must be supported

- stale decision applied to outdated node version
- human chooses illegal transition
- multiple pending gates conflict
- gate resolved but resume safety is no longer valid

## Completion rule

Human intervention is a first-class, auditable runtime path rather than an off-the-record manual workaround.
