# Hook System Decisions

## Scope landed in this phase

- Hook expansion is now a compile-time compiler stage, not a daemon-time side-effect system.
- Effective policy hook refs and explicit node hook refs are resolved into explicit compiled subtasks.
- Hook inspection is now daemon-backed through `workflow hooks --node <id>` and `workflow hooks --workflow <id>`.

## Deliberate boundaries

- Only workflow-shaping insertion triggers are materialized in this slice.
- `on_node_created` and `on_merge_conflict` remain runtime-only concepts and are recorded as skipped hook diagnostics during compilation.
- Hook `if` conditions are not yet evaluated. Any hook with non-empty conditional clauses is skipped with an explicit reason.

## Ordering rule implemented

- Expansion is deterministic by insertion phase first.
- Within an insertion phase, built-in sources sort before project sources.
- Final ordering is by relative path and hook id.

## Persistence and auditability

- Hook diagnostics are persisted in `compiled_workflows.resolved_yaml.hook_expansion`.
- Expanded subtasks are marked with `compiled_subtasks.inserted_by_hook = true`.
- `compiled_subtasks.inserted_by_hook_id` is a deterministic UUID derived from hook source path and expanded subtask key.
- Node-version source lineage now captures selected hook documents and prompt templates referenced by those hooks.

## Follow-up work still deferred

- Conditional hook selection against changed-entity context.
- Dedicated persistence for hook-selection diagnostics if `resolved_yaml` inspection becomes insufficient.
- Broader support for runtime-only hook triggers outside workflow compilation.
