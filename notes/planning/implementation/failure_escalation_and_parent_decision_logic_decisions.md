# Failure Escalation And Parent Decision Logic Decisions

## Scope

F25 implements the first durable parent-decision loop for child failures.

## Decisions

1. Total and consecutive parent child-failure counters remain on `node_run_state`, while per-child counters now live in `node_run_child_failure_counters`.
2. Parent decision history is persisted in `workflow_events` with `event_scope = parent_decision` instead of adding a new dedicated decision table in the first slice.
3. The first follow-on expansion now widens the automatic failure taxonomy to include `manual_tree_conflict`, `rectification_failure`, and `provider_recovery_failure` in addition to the original `validation_failure`, `review_failure`, `test_failure`, `merge_conflict_unresolved`, `bad_layout_or_bad_requirements`, `dependency_or_context_failure`, `environment_failure`, `transient_execution_failure`, and `unknown_failure` classes.
4. `retry_child` is currently implemented as a durable child reset back to `READY` plus authority-mirror clear, not as automatic immediate rerun admission.
5. `regenerate_child` now records the decision first and then invokes the existing regeneration pipeline after commit so rebuild lineage remains durable and queryable.
6. `replan_parent` is currently modeled as a user-gated parent pause with `pause_flag_name = parent_replan_required` and the packaged `runtime/parent_local_replan.md` prompt.
7. Threshold exhaustion and fallback ambiguity currently pause the parent with `pause_flag_name = parent_child_failure_pause` and the packaged `runtime/parent_pause_for_user.md` prompt.
8. The daemon-authority compatibility constraints were widened in this slice so retry-reset mutations may durably record `node.run.retry.reset` and a `ready` mirror state.
9. Parent decision payloads now carry explicit matrix details: `failure_origin`, `classification_reason`, `decision_reason`, `options_considered`, `threshold_triggered`, `threshold_reason`, and the frozen policy snapshot used for the choice.

## Deferred Work

- Parent-local replanning still reuses pause context and workflow-event payloads instead of writing a dedicated durable parent summary artifact table.
- Automatic retry admission after `retry_child` remains deferred; operators or later automation still need to start the replacement child run explicitly.
- Multi-child structural heuristics remain intentionally simple in this slice; broader sibling-aware replanning and dependency-critical child weighting can extend the same counter and event surfaces later.
