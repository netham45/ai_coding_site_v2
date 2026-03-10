## Phase

`plan/features/53_F03_override_resolution_compile_stage.md`

## Decision

Expose override resolution as a dedicated compiler-stage read under the `workflow` namespace, while preserving the existing `yaml override-chain` artifact-oriented surface.

## Why

- The override fold itself was already implemented and persisted in the compiled workflow payload.
- The missing piece for this slice was stage-oriented visibility: source-discovery and schema-validation now have explicit compiler-stage reads, and override resolution needed the same treatment.

## Implementation notes

- Added daemon-backed reads:
  - `GET /api/nodes/{id}/workflow/override-resolution`
  - `GET /api/workflows/{id}/override-resolution`
- The payload exposes:
  - applied override count
  - warning count
  - applied override records
  - warnings
  - resolved-document count and inventory
- `yaml override-chain` remains the narrower YAML/artifact-facing surface; `workflow override-resolution` is the compiler-stage inspection view.
