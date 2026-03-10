## Phase

`plan/features/52_F03_schema_validation_compile_stage.md`

## Decision

Expose schema validation as a dedicated compiler-stage inspection surface over the existing compile pipeline, instead of creating a separate persistence layer for successful validation artifacts.

## Why

- The actual validation gate already exists in the compiler and already persists failures as `compile_failures` with `failure_stage = schema_validation`.
- What was missing was a clean way to inspect the successful side of that stage for one compiled workflow without opening the entire compiled payload or inferring it from raw source rows.

## Implementation notes

- Added daemon-backed reads:
  - `GET /api/nodes/{id}/workflow/schema-validation`
  - `GET /api/workflows/{id}/schema-validation`
- The payload exposes:
  - compiled workflow identity
  - validated-document count
  - per-family counts
  - validated documents in deterministic source order
- CLI surface:
  - `workflow schema-validation --node <id>`
  - `workflow schema-validation --workflow <id>`

## Deferred

- Successful schema-validation artifacts are still derived from the compiled workflow's discovered-source snapshot rather than stored in a separate table.
- If operators later need per-document validation warnings or normalization traces, add them to this stage surface before introducing another durable artifact family.
