# Prompt History And Summary History Decisions

## Scope boundary

- This slice persists prompt deliveries and summary registrations as durable audit rows without changing the compiled-workflow model.
- Prompt delivery is recorded when the daemon serves `subtask prompt`, not when the workflow is compiled.
- Summary history is recorded when `summary register` succeeds, not when a subtask is completed.

## Durable records

- `prompts` stores the rendered content the session actually retrieved, plus frozen source identity from the compiled subtask: `source_subtask_key`, `template_path`, and `template_hash`.
- `summaries` stores the registered summary body, content hash, summary taxonomy, and active attempt linkage.
- The existing `registered_summaries` mirror on `subtask_attempts.output_json` remains in place for compatibility with already-implemented runtime and validation flows.

## CLI surface

- Packaged prompt asset inspection remains under `prompts show`.
- Durable prompt history is exposed separately via `prompts history --node <id>` and `prompts delivered-show --prompt <id>`.
- Durable summary history is exposed via `summary history --node <id>` and `summary show --summary <id>`.

## Validation interaction

- `summary_written` validation now accepts either the compatibility mirror on the attempt payload or the durable `summaries` row.
- This keeps older execution paths valid while making the durable table authoritative for audit and later reproducibility work.
