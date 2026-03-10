# Documentation Generation Decisions

## Scope implemented in this slice

- Added durable `documentation_outputs` persistence for generated docs views.
- Added daemon-backed node and tree docs build/list/show surfaces.
- Added CLI commands for docs build/list/show.
- Added deterministic markdown rendering from durable runtime state, summary history, prompt history, review/testing summaries, tree inspection, and provenance rationale.

## Key implementation decisions

- Documentation generation is currently deterministic daemon rendering, not prompt-driven generation.
- The packaged YAML family continues to use `docs_definition` as the concrete document kind even though some planning notes still describe the concept as `documentation_definition`.
- Node builds are bounded to the canonical scope set `local`, `entity_history`, and `custom`.
- Tree builds are bounded to the canonical scope set `merged`, `rationale_view`, and `custom`.
- Docs builds now backfill the canonical built-in definitions for the requested scope set even when effective project policy only references a narrower custom docs view.

## Deferred work

- Prompt-driven authored documentation generation remains deferred.
- Automatic rebuild triggers on finalize, rectify, or merge remain deferred.
- A separate docs build-event table remains deferred because append-only `documentation_outputs` rows are sufficient for the current audit surface.
