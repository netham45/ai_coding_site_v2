# Phase S02: Python Foundation

## Goal

Create the shared Python foundations used by both daemon and CLI.

## Scope

- Database: integrate shared config and DB resource management.
- CLI: establish command registration, config loading, and error formatting.
- Daemon: establish app boot, dependency injection, logging, configuration boundaries, and sync-DB-on-async-request handling expectations using FastAPI + Uvicorn as the default API/server stack.
- YAML: add resource-loading interfaces for future schema and built-in definitions.
- Prompts: add prompt/resource loading interfaces.
- Tests: exhaustively test config loading, environment parsing, logging setup, dependency wiring, failure modes, and auth-token loading helpers.
- Performance: benchmark startup overhead for CLI and daemon boot and measure sync DB request handling overhead assumptions.
- Notes: update setup notes if package or app-structure choices affect later implementation.

## Exit Criteria

- CLI and daemon share stable Python foundations.
- startup behavior is testable and reproducible.
