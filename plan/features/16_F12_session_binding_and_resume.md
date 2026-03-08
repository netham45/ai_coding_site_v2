# Phase F12: Session Binding And Resume

## Goal

Bind one authoritative session to one active run and support safe resume/reattach behavior.

## Scope

- Database: primary session binding, session status, session events, run/session linkage.
- CLI: bind, attach, resume, show-current, and session-inspection surfaces.
- Daemon: authoritative session binding and safe reattachment behavior.
- YAML: runtime policy only; binding logic remains code-owned.
- Prompts: session bootstrap prompt aligned with actual command loop.
- Tests: exhaustive single-session, detached-session, invalid-bind, and durable-history coverage.
- Performance: benchmark heartbeat and lookup paths.
- Notes: update session notes if tmux/provider integration needs stronger abstractions.
