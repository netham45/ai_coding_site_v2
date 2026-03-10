# Session Binding And Resume Decisions

## Scope

This note records the implementation decisions for `plan/features/16_F12_session_binding_and_resume.md`.

## Decisions

- durable primary session ownership now lives in `sessions` and `session_events`, keyed to the authoritative node version and active `node_run_id`
- `session bind --node <id>` now requires an admitted active run; the daemon will not create a session binding for nodes that are not already in live execution
- only one active primary session is allowed per active run; bind/attach/resume reuse that session when the harness session still exists
- if the durable primary session record exists but the harness session is missing, attach/resume invalidate the old session row as `LOST`, preserve its history, and create a replacement primary session record
- `session show-current` now resolves from the durable primary-session record rather than only from the harness adapter’s latest session snapshot
- `session show`, `session list`, and `session events` are now real inspection commands backed by durable session records and append-only session events

## Deferred work

- pushed-child-session ownership and `child_session_results`
- richer provider-specific recovery and rebinding beyond tmux/fake session names
- durable nudge/control commands and heartbeat event history
- stronger recovery classification taxonomy and explicit recovery-status surfaces

## Notes impact

- runtime notes now treat primary session binding as a run-owned durable record rather than a harness-only side effect
- database notes now describe the current status vocabulary as an implemented durable surface
- recovery notes now map attach/resume to explicit durable reuse-or-replacement behavior
