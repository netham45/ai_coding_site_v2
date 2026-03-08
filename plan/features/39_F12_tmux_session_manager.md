# Phase F12-S1: tmux Session Manager

## Goal

Implement the concrete tmux-backed session manager used for active runs.

## Scope

- Database: persist tmux session identity, linkage to node run/session records, and relevant events.
- CLI: implement session attach/show/resume behavior that understands tmux-backed sessions.
- Daemon: create and manage tmux sessions per task/run GUID, launch provider processes, and keep session identity authoritative.
- YAML: runtime policy may configure tmux-related limits, but tmux management remains code-owned.
- Prompts: ensure session bootstrap prompts match the real tmux-backed session lifecycle.
- Tests: exhaustively cover tmux session creation, attachment, missing tmux sessions, duplicate-session detection, and session record consistency.
- Performance: benchmark tmux session creation and attach/reattach overhead.
- Notes: update tmux/session notes if implementation forces naming or lifecycle changes.
