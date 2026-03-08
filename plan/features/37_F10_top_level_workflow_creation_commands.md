# Phase F10-S1: Top-Level Workflow Creation Commands

## Goal

Implement prompt-driven creation commands such as `ai-tool workflow start --kind <type> --prompt <prompt>` and equivalent node-creation entrypoints.

## Scope

- Database: persist prompt-driven request inputs, initial node version, initial compiled workflow binding, and start metadata.
- CLI: implement top-level create/start commands for arbitrary supported node kinds.
- Daemon: resolve the requested kind, create the top-level node version, compile it, and optionally start the run.
- YAML: ensure node definitions are discoverable for prompt-driven top-level creation.
- Prompts: bind the incoming user prompt to initial node creation and main prompt context correctly.
- Tests: exhaustively cover valid create flows, bad kinds, missing prompt cases, compile failures on create, and create-without-run versus create-and-run behavior.
- Performance: benchmark create/start latency, especially compile-on-create overhead.
- Notes: keep getting-started and top-level creation notes aligned with the real command surface.
