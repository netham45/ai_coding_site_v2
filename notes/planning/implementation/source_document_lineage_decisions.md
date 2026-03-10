# Source Document Lineage Decisions

## Summary

Phase F27 adds durable source-document capture for node versions, with current staging focused on built-in YAML and prompt-template inputs that are already real in the repo.

## Decisions

- Added `source_documents` for durable source text plus content hashes.
- Added `node_version_source_documents` for version-to-source lineage edges and stable resolution order.
- Captured lineage automatically when authoritative `v1` is created through daemon node creation.
- Captured lineage automatically when a superseding candidate version is created.
- Exposed lineage through `node sources`, `node version sources`, and `workflow sources --node`.
- Added missing built-in prompt-template files referenced by node YAML so prompt lineage is no longer dangling.

## Why

- Reproducibility requires exact source text and hashes, not only paths.
- Version lineage is already durable, so source lineage now belongs on the version record rather than the mutable logical node.
- The repo already had meaningful built-in node/task/layout/policy/prompt inputs, so this slice can persist real compile-adjacent lineage now without waiting for full immutable workflow compilation.

## Deferred

- Project-local extensions and overrides in the resolved source chain.
- Persisted resolved-merge YAML snapshots.
- Hook-inserted source lineage and compiled workflow hashes.
- Workflow-id-based source lookup before compiled workflows exist.
