# Validation Framework Decisions

## Scope

F21 implements validation as a durable runtime gate without pulling review/testing/docs execution forward.

## Decisions

1. Validation results are persisted in a dedicated `validation_results` table instead of only embedding gate output inside `subtask_attempts.validation_json`.
2. `subtask_attempts.validation_json` remains the latest per-attempt cache, while `validation_results` is the authoritative history surface.
3. The default built-in node workflows now include `validate_node` after `execute_node`, making validation part of the compiled default task chain.
4. The compiler now preserves the authored first subtask type, prompt, command, checks, outputs, and retry policy for each task instead of flattening everything to `run_prompt`.
5. The daemon evaluates validation gates during `workflow advance` when the current compiled subtask type is `validate`; a failed required check marks the run failed and blocks completion.
6. F21 only implements the validation family directly. Review/testing/docs remain later dedicated phases, but the runtime and DB surfaces are now shaped to stay aligned with those later result families.

## Current Validation Coverage

- `command_exit_code`
- `summary_written`
- `file_exists`
- `file_updated`
- `file_contains`
- `docs_built`
- `provenance_updated`

Additional validation families should extend the daemon evaluator and update the notes in the same change.
