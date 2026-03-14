You have missed at least one expected progress signal for the current subtask.

The idle nudge gate has already fired. Do not keep waiting for another trigger.

Immediately:
- follow the concrete current-stage action in this nudge instead of reloading the prompt again by default
- if the current-stage action is genuinely unclear, fetch the live current subtask prompt with `{{prompt.cli_command}}` exactly once
- your next response must be an `exec_command` tool call, not prose
- report the concrete next action by doing it, or fail safely with a bounded summary

Do not stay silent.
