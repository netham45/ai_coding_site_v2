# Flow 08: Handle Failure And Escalate

## Purpose

Handle subtask, child, dependency, or structural failure in a way that is visible, bounded, and actionable.

## Covers journeys

- subtask failure
- child failure affecting a parent
- impossible dependency wait
- repeated retry exhaustion

## Entry conditions

- a subtask, node, child, dependency, or compile path has failed or become impossible to complete

## Task flow

1. classify the failure type
2. persist evidence, summary, and attempt context
3. increment relevant retry/failure counters
4. determine whether the failure is retryable, pausable, or escalatory
5. if dependency-related, detect whether the wait is impossible under current graph state
6. if child-related, invoke parent failure decision logic
7. if thresholds are exceeded, pause for user or replan
8. publish blocker/failure status through read surfaces

## Required subtasks

- `classify_failure`
- `persist_failure_summary`
- `update_retry_and_threshold_counters`
- `evaluate_retry_eligibility`
- `detect_impossible_wait_if_needed`
- `invoke_parent_decision_logic_if_needed`
- `pause_or_replan_if_needed`
- `publish_failure_read_model`

## Required capabilities

- `ai-tool subtask fail ...`
- `ai-tool subtask retry ...`
- parent failure decision logic
- dependency impossible-wait detection
- failure and pause event persistence
- blocker inspection surfaces

## Durable outputs

- failure summaries
- updated subtask attempt status
- updated run and node state
- parent decision event or escalation event
- impossible-wait classification if applicable

## Failure cases that must be supported

- repeated AI execution failure
- validation/review/testing rejection
- child failure with upstream implications
- invalid dependency target or deadlock
- policy threshold exhaustion

## Completion rule

No failure remains an opaque stuck state; it is always classified, persisted, and routed into retry, pause, replan, or escalation.
