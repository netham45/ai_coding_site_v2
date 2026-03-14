Your session appears idle on node `{{node_id}}`.

This message is the real idle nudge. Any earlier instruction that said to wait for the nudge is now satisfied. Do not keep waiting.

Immediately:
- follow the concrete current-stage action in this nudge instead of reloading the prompt again by default
- if the current-stage action is genuinely unclear, fetch the live current subtask prompt with `{{prompt.cli_command}}` exactly once
- your next response must be an `exec_command` tool call, not prose
- either continue with the concrete next step for the active stage or report a bounded failure summary

Do not stay silent and do not switch to unrelated work.
