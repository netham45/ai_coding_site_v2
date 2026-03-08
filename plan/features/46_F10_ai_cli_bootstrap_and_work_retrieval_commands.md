# Phase F10-S3: AI CLI Bootstrap And Work Retrieval Commands

## Goal

Implement the AI-facing CLI command family for discovering current work.

## Scope

- Database: ensure work-retrieval state is durably queryable.
- CLI: implement:
  - `session bind`
  - `session show-current`
  - `workflow current`
  - `subtask current`
  - `subtask prompt`
  - `subtask context`
- Daemon: validate retrieval requests against authoritative run/session state.
- YAML: no new semantics beyond compiled bindings and context categories.
- Prompts: bootstrap prompts must match the actual retrieval commands.
- Tests: exhaustively cover missing-run, wrong-session, stale-session, and valid retrieval behavior.
- Performance: benchmark hot prompt/context retrieval latency.
- Notes: update CLI/runtime notes if retrieval response shapes evolve.
