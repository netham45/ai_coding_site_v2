# Optional Pushed Child Sessions Decisions

## Scope

This note records the implementation boundary for `plan/features/19_F14_optional_pushed_child_sessions.md`.

## Decisions

- No new migration was required in this phase. The existing `sessions.parent_session_id` and `child_session_results` tables were sufficient for the first bounded child-session slice.
- `session push --node <id> --reason <reason>` now creates a durable `pushed_child` session linked to the active primary session for the same run.
- `session pop --session <id> --file <path>` now expects a structured JSON merge-back artifact rather than a plain summary file.
- Merge-back validation currently enforces a bounded result shape: `status`, `summary`, optional `findings`, optional `artifacts`, and optional `suggested_next_actions`.
- Canonical durability remains in `child_session_results`.
- The parent-context attachment is staged by projecting the validated child-session payload into the current parent subtask context, so `subtask context --node <id>` exposes returned child work immediately.
- Pushed child sessions do not change parent cursor ownership and do not auto-advance the parent workflow.

## Deferred Work

- Dedicated child-session recovery and replacement behavior remains a later slice.
- Background automation that decides when to push child sessions remains deferred; this phase only implements explicit operator/AI surfaces.
- Richer artifact validation and file-existence checks remain deferred beyond the current structured payload validation.
