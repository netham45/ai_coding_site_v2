## Phase 46: AI CLI Bootstrap And Work Retrieval Commands

- The read-side AI bootstrap command family was already present, so this slice tightened the session-discovery contract instead of introducing duplicate commands.
- `session show-current` is now treated as the authoritative first bootstrap read: it returns the durable logical-node binding (`logical_node_id`, `node_kind`, `node_title`), the current `run_status`, and the derived `recovery_classification`.
- Recovery classification is computed directly from the durable run/session state plus live tmux inspection, so bootstrap code can distinguish healthy, stale-but-recoverable, and other degraded bindings before calling `workflow current` or `subtask ...`.
- `workflow current`, `subtask current`, `subtask prompt`, and `subtask context` remain node-scoped retrieval commands; this slice did not add a separate implicit-current-node lookup path because `session show-current` now provides the safe node selector explicitly.
- Prompt/bootstrap assets were updated to instruct sessions to inspect `session show-current` first, keeping prompt expectations aligned with the actual retrieval flow.
