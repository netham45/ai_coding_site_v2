# Override And Merge Resolution Decisions

## Scope landed in this slice

- `override_definition` is now a validated YAML family loaded from the packaged project-local override root.
- The compiler now runs an explicit `override_resolution` stage before policy resolution and durable workflow persistence.
- Applied overrides, compatibility warnings, and resolved per-document YAML now persist in `compiled_workflows.resolved_yaml`.
- CLI and daemon inspection now expose `yaml override-chain` and `yaml resolved` against compiled workflows.

## Deliberate staging boundaries

- Override merging is currently bounded to top-level family fields with explicit field-level merge modes.
- Identity fields such as document `id` and node `kind` are currently treated as immutable during override resolution.
- The current override source set is the packaged override root as a deterministic compile input boundary; narrower node-scoped applicability rules remain deferred.
- Standalone path-based override diff tooling remains deferred; current inspection is workflow-centric and audit-oriented.

## Durability stance

- No new override-specific tables were introduced in this slice.
- Override lineage uses existing `source_documents` and `node_version_source_documents`.
- Override conflicts use existing durable `compile_failures` records with `failure_stage = override_resolution` and structured target metadata.
