# Hook Expansion And Policy Resolution Compile Stage Decisions

## Decision

Phase `54_F03_hook_expansion_and_policy_resolution_compile_stage` is implemented as an explicit inspection surface over the already-frozen compiled workflow snapshot rather than as a second persistence layer.

## Why

- hook selection, skipped-hook diagnostics, expanded steps, effective policy, and policy impact are already durably frozen in `compiled_workflows.resolved_yaml`
- exposing that state directly keeps the compile-stage contract inspectable without duplicating authority
- the stage boundary stays aligned with the compile ordering documented in the F03 notes: source discovery, schema validation, override resolution, hook and policy fold, then rendering

## Implementation Shape

- daemon endpoints:
  - `GET /api/nodes/{id}/workflow/hook-policy`
  - `GET /api/workflows/{id}/hook-policy`
- CLI command:
  - `ai-tool workflow hook-policy --node <id>|--workflow <id>`
- payload includes:
  - `effective_policy`
  - `policy_impact`
  - `selected_hooks`
  - `skipped_hooks`
  - `expanded_steps`

## Deliberate Non-Changes

- no new database table or migration was needed for this phase
- the pre-existing `workflow hooks` surface remains as the narrower hook-only view
