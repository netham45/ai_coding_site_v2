# Phase F14: Optional Pushed Child Sessions

## Goal

Support bounded child sessions for research, review, and verification without transferring node ownership.

## Scope

- Database: child session records, parent linkage, merge-back payloads.
- CLI: push/pop/show child-session commands.
- Daemon: bounded delegation, session launch, merge-back validation.
- YAML: declarative child-session subtask patterns.
- Prompts: delegated research/review/verification prompts.
- Tests: exhaustive push, merge-back, invalid return, and parent-cursor ownership coverage.
- Performance: benchmark child-session launch and merge-back overhead.
- Notes: update child-session contract notes if payload shape changes.
