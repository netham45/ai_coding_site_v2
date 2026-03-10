# Stage Context Retrieval And Startup Context Decisions

## Scope implemented in this slice

- Extended `subtask prompt` and `subtask context` to expose a daemon-assembled `stage_context_json` bundle.
- Added stage-context assembly from durable startup metadata, compiled-stage metadata, dependency state, recent prompt/summary history, and cursor-carried child/reconcile state.
- Added unit, daemon-integration, CLI-integration, and performance coverage for the richer stage-start context.

## Key implementation decisions

- This slice does not add a new table. Stage-start context is assembled from existing durable state:
  - `node_versions`
  - `node_runs` and `node_run_state`
  - `compiled_subtasks`
  - `node_dependencies` and `node_dependency_blockers`
  - prompt and summary history
  - execution-cursor overlays such as child-session results and parent reconcile context
- The existing `input_context_json` compatibility surface stays in place, but now also carries `stage_context_json` so existing consumers can opt into the richer bundle without switching endpoints.
- `subtask prompt` and `subtask context` expose the same assembled context categories so stage-start retrieval is consistent across prompt-first and context-first clients.

## Boundaries kept in place

- The bundle is read-only assembly, not a new durable authority.
- Dependency context is currently node-version scoped, not subtask-specific semantic dependency reasoning.
- Prompt history is intentionally recent-run scoped rather than a full historical transcript export.

## Deferred work

- YAML-declared per-subtask context-category requirements remain deferred; the current bundle is a standard default set.
- More selective context pruning and prompt-family-specific context shaping remain deferred.
- Repo/codebase inspection context is still handled by the prompt and execution layers rather than being injected wholesale into stage-start context.
