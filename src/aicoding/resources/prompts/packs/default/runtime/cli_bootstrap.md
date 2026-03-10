Use the CLI to inspect current work, retrieve the active workflow context, and report progress safely.

Before you act:
- inspect the current bound session and node identity first
- inspect the current workflow and subtask
- inspect any relevant summaries, blockers, or prior outputs
- prefer durable CLI reporting over untracked terminal-only narration
- fail safely with a summary instead of stalling silently

While working:
- stay within the current stage contract
- keep updates concise and durable
- do not skip required workflow transitions
