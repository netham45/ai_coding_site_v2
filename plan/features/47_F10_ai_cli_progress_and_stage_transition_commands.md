# Phase F10-S4: AI CLI Progress And Stage Transition Commands

## Goal

Implement the AI-facing CLI command family for stage progress and transition control.

## Scope

- Database: ensure progress mutations and stage transitions are durable and ordered correctly.
- CLI: implement:
  - `subtask start`
  - `subtask heartbeat`
  - `subtask complete`
  - `subtask fail`
  - `summary register`
  - `workflow advance`
  - `workflow pause`
  - `workflow resume`
- Daemon: validate transition legality and accept or reject completion authoritatively.
- YAML: transition behavior remains code-owned; YAML only supplies stage contracts and policy.
- Prompts: correction/missed-step prompts must align with the real progress commands.
- Tests: exhaustively cover valid completion, rejected completion, bad transitions, duplicate calls, and pause/fail behavior.
- Performance: benchmark high-frequency progress-command paths.
- Notes: update CLI/runtime docs if transition semantics tighten during implementation.
