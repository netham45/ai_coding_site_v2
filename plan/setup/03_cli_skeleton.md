# Phase S03: CLI Skeleton

## Goal

Create the initial Python CLI surface and command-group structure.

## Scope

- Database: wire read-only and health-check DB access into CLI infrastructure.
- CLI: create command namespaces for workflow, node, subtask, session, yaml, prompts, docs, and admin/debug.
- Daemon: define daemon-client boundary for mutating commands.
- YAML: prepare source/resolved YAML inspection command hooks.
- Prompts: prepare prompt inspection command hooks.
- Tests: exhaustively test command registration, help output, config resolution, argument parsing, and daemon-unavailable handling.
- Performance: benchmark cold-start and hot-start command latency.
- Notes: update CLI notes if command grouping changes from the spec.

## Exit Criteria

- CLI command tree exists and is testable even before full implementation.
