# Phase F10-S2: Stage Context Retrieval And Startup Context Assembly

## Goal

Assemble and expose the exact stage context an active session needs at stage start.

## Scope

- Database: persist or derive prompt/context inputs, dependency summaries, child summaries, prior summaries, and relevant result references.
- CLI: implement reliable `current`, `prompt`, and `context` retrieval surfaces with structured output.
- Daemon: build authoritative stage-start context from durable state rather than terminal history.
- YAML: declaratively identify which context categories a task/subtask expects where needed.
- Prompts: make prompt payloads explicitly reference dependency summaries, child summaries, and prior relevant results.
- Tests: exhaustively cover startup context composition, missing-context cases, dependency summary injection, and child-summary visibility.
- Performance: benchmark repeated context assembly and retrieval for hot stages.
- Notes: clarify stage-start context rules in runtime and journey notes if implementation reveals missing categories.
