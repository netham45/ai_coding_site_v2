## Phase 56: Compiled Workflow Persistence And Failure Diagnostics

- Most compiled-workflow persistence was already implemented before this slice. The remaining gap was the persistence tail: unexpected exceptions during final compiled-artifact writes could escape without being converted into a durable compile-failure record.
- The compiler now wraps unexpected persistence-stage exceptions as `failure_stage = workflow_persistence` and `failure_class = workflow_persistence_failure`.
- Because compilation still runs inside a nested transaction, those persistence failures roll back partial `compiled_workflows`, `compiled_tasks`, `compiled_subtasks`, and dependency rows before the durable `compile_failures` record is written.
- Existing stage-specific `WorkflowCompileError` failures remain unchanged; this slice only hardens the unexpected-exception path so operator inspection and auditability stay consistent.
