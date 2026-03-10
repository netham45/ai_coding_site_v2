# Failure Taxonomy And Parent Decision Matrix Decisions

## Scope

F25 follow-on work expands the first durable parent-decision slice into a more explicit runtime decision matrix.

## Decisions

1. The failure taxonomy is now intentionally broader in daemon code than in the original first-slice note set. The runtime currently distinguishes `validation_failure`, `review_failure`, `test_failure`, `merge_conflict_unresolved`, `manual_tree_conflict`, `rectification_failure`, `bad_layout_or_bad_requirements`, `dependency_or_context_failure`, `environment_failure`, `transient_execution_failure`, `provider_recovery_failure`, and `unknown_failure`.
2. Failure classification now uses more than summary text. The daemon also considers the failed subtask identity, durable quality-gate payloads, and lifecycle/dependency context before choosing the class.
3. Parent decision payloads now carry explicit matrix reasoning rather than just the chosen action. The current response and history payloads expose `failure_origin`, `classification_reason`, `decision_reason`, `options_considered`, `threshold_triggered`, `threshold_reason`, and the frozen threshold policy snapshot used for the choice.
4. The current automatic matrix intentionally remains conservative. `provider_recovery_failure` and `unknown_failure` pause for user guidance, while merge and rectification failures regenerate the child and quality/input failures replan at the parent.
5. The richer matrix is implemented entirely in daemon logic and `workflow_events` payloads in this slice. No new table was introduced because the durable counter/state family already exists and the additional reasoning is append-only event metadata.

## Deferred Work

- Multi-child heuristics remain narrow. The current matrix still does not weight sibling completion state, dependency centrality, or cluster-wide failure patterns strongly enough to replace user judgment in broader tree failures.
- The flow-suite coverage still exercises only a subset of the matrix. Additional flow variants should be added before this area is considered exhaustively scenario-tested.
- Automatic retry admission after `retry_child` remains deferred; this slice still resets the child durably and leaves re-admission to later automation or the operator.
