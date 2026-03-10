# Review Framework Decisions

## Scope

F22 implements review as a durable typed quality gate with explicit pass, revise, and fail routing.

## Decisions

1. Review results are persisted in a dedicated `review_results` table instead of relying only on free-form summaries.
2. `subtask_attempts.review_json` is the latest per-attempt cache, while `review_results` is the durable history surface.
3. The default built-in node workflows now include `review_node` after `validate_node`, making review part of the compiled default task chain.
4. The daemon evaluates review gates during `workflow advance` when the current compiled subtask type is `review`; the gate persists structured review rows before routing pass, revise, or fail behavior.
5. The current `revise_action` implementation rewinds to the last non-gate implementation subtask so validation and review both rerun on the next pass.
6. The CLI exposes both inspection (`review show`, `review results`) and a structured mutation surface (`review run`) so review outcomes do not need to be hidden inside ad hoc prompt prose or raw API calls.
7. Source-lineage capture now includes referenced review definitions and their prompt templates when built-in tasks declare `uses_reviews`.

## Current Review Outcome Handling

- `pass`/`passed`: continue
- `revise`: follow the review definition's revise action, currently implemented as daemon-owned rewind or pause
- `fail`/`failed`: follow the review definition's fail action, currently implemented as pause-for-user or fail-to-parent

Testing, docs, and user-override handling remain their own later phases and should extend this same typed quality-gate pattern rather than replacing it.
