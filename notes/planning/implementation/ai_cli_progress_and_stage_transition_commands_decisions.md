## Phase 47: AI CLI Progress And Stage Transition Commands

- The core AI-facing progress and transition commands were already daemon-backed before this slice, so the remaining work focused on contract alignment and verification rather than new write endpoints.
- `subtask start`, `subtask heartbeat`, `subtask complete`, `subtask fail`, `summary register`, `workflow advance`, `workflow pause`, and `workflow resume` remain explicit daemon-owned mutations; attempt completion still does not implicitly advance the workflow cursor.
- The CLI now supports the documented `subtask fail --summary-file <path>` path in addition to the older inline `--summary` compatibility form. The CLI reads the file locally and sends the resulting content as the durable failure summary.
- Heartbeat semantics were clarified in notes: heartbeat persistence already exists today as active-attempt and run-cursor metadata, while a separate append-only heartbeat history table remains deferred.
- This slice deliberately did not move pause, approval, or failure-routing policy into YAML. Stage contracts still come from compiled workflow data, while transition legality remains code-owned in the daemon.
