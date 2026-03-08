# Phase S06: tmux And Session Test Harness

## Goal

Create the tmux-aware development and test harness used by the later session, idle, and recovery phases.

## Scope

- Database: prepare test helpers for session-event and heartbeat persistence.
- CLI: create harness hooks for attach/resume/show-current style session testing.
- Daemon: add tmux adapter abstraction, fake session runner, and polling test seams.
- YAML: no new YAML semantics; runtime policy hooks only.
- Prompts: prepare prompt fixtures for bootstrap/nudge/recovery flows.
- Tests: exhaustively test tmux adapter abstraction, fake-session creation, alt-screen capture hooks, and deterministic idle simulation helpers.
- Performance: benchmark polling overhead and session harness startup cost.
- Notes: update session/recovery notes if tmux integration requires stronger abstractions or constraints.

## Exit Criteria

- tmux-backed and fake-session-backed tests can be written deterministically.
