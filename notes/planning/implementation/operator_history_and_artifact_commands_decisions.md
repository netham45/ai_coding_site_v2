## Phase

`plan/features/49_F11_operator_history_and_artifact_commands.md`

## Decision

Finish the missing artifact/history CLI gap by making `yaml sources` a real daemon-backed artifact inspection surface for nodes and workflows, while preserving the older packaged-resource inventory mode behind `--scope`.

## Why

- Most of the phase-49 command family was already delivered under earlier feature slices:
  - prompt history
  - summary history
  - docs list/show/build
  - provenance/rationale/entity inspection
  - merge history
  - rebuild history
  - resolved YAML inspection
- The remaining mismatch was that `yaml sources` still returned only local resource root paths instead of actual persisted compile/source lineage for nodes and workflows.

## Implementation notes

- `yaml sources --node <id>` now calls the daemon-backed node source-lineage surface.
- `yaml sources --workflow <id>` now calls the daemon-backed compiled-workflow source surface.
- `yaml sources --scope <scope>` remains available for local packaged resource discovery and is treated as the non-daemon fallback mode.

## Deferred

- If operators need richer family/path filtering over source-lineage bundles, add daemon query parameters instead of reimplementing that filtering in the CLI.
