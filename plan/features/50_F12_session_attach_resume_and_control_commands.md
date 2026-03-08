# Phase F12-S2: Session Attach, Resume, And Control Commands

## Goal

Implement the CLI command family for active session control.

## Scope

- Database: ensure session control operations have durable event and current-state backing.
- CLI: implement:
  - `session show`
  - `session events`
  - `session attach`
  - `session resume`
  - `session nudge`
- Daemon: validate attach/resume/control semantics and maintain authoritative session ownership.
- YAML: runtime policy only.
- Prompts: session-control prompts must align with actual session-control commands.
- Tests: exhaustively cover attach/resume/nudge semantics, invalid-control attempts, and authority conflicts.
- Performance: benchmark session-control command latency.
- Notes: update session CLI notes if control surfaces evolve.
