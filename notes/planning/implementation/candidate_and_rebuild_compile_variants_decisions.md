# Candidate And Rebuild Compile Variants Decisions

## Summary

Feature `63_F03_candidate_and_rebuild_compile_variants` promotes non-authoritative compile targets into first-class operator-visible compile variants without introducing a second compiler.

## Decisions

- Reuse the existing immutable compiler entry point `compile_node_version_workflow(...)` rather than creating a separate candidate or rebuild compiler.
- Treat compile target mode as daemon-owned runtime context, not YAML state.
- Derive compile variant from durable node-version status plus rebuild lineage:
  - `authoritative`
  - `candidate`
  - `rebuild_candidate`
- Persist that derived compile context inside the compiled workflow snapshot `resolved_yaml.compile_context` so the variant is frozen with the compiled artifact.
- Mirror the same compile context into durable compile-failure payloads via `compile_failures.details_json.compile_context` so failed candidate/rebuild compiles remain inspectable without a separate schema change.
- Expose version-targeted workflow inspection and compile invocation through daemon and CLI surfaces using `--version` and `/api/node-versions/{version_id}/workflow/...`.

## Why No Migration

No new table or column was required for this slice.

Reason:

- compiled workflows already bind to `node_version_id`
- compile failures already bind to `node_version_id`
- rebuild lineage already exists durably through `rebuild_events`

That is enough to derive and freeze compile-mode context safely.

## Remaining Boundary

This phase makes candidate and rebuild compile first-class and inspectable.

It does not yet change live cutover execution or git finalize behavior. Those remain covered by later git-focused phases.
