## Phase

`plan/features/51_F03_source_discovery_and_loading_pipeline.md`

## Decision

Close this slice by making the compiler's first stage directly inspectable, rather than restructuring the already-working load path.

## Why

- The compiler already discovers and loads compile inputs deterministically through captured source documents, ordered `resolution_order`, and explicit override resolution.
- The real missing piece was observability: operators could inspect final workflow sources and resolved YAML, but not the stage-local discovery order and resolved-document inventory as one coherent first-stage view.

## Implementation notes

- Added daemon-backed source-discovery reads:
  - `GET /api/nodes/{id}/workflow/source-discovery`
  - `GET /api/workflows/{id}/source-discovery`
- The returned payload exposes:
  - compiled workflow identity
  - node version and logical node identity
  - workflow source hash
  - built-in library version
  - deterministic discovery order with explicit ordinals
  - resolved-document inventory copied from the compiled workflow payload
- The CLI surface is:
  - `workflow source-discovery --node <id>`
  - `workflow source-discovery --workflow <id>`

## Deferred

- Stage-specific durable discovery-failure records remain represented through the existing `compile_failures` surface rather than a separate table.
- If future source categories diverge from the current captured-source model, revisit whether source discovery should persist its own stage artifact instead of deriving from compiled workflow and source-document tables.

## Performance note

- The full-suite baseline for `workflow source-discovery` lookup is currently volatile enough that the performance guard is set to `< 0.5s` rather than `< 0.4s`; keep treating materially larger regressions as suspicious, but avoid failing on ordinary CI and local variance around the low-400ms range.
