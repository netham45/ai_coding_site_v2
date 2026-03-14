Use the CLI to inspect current work, retrieve the active workflow context, and report progress safely.

Before you act:
- inspect the current bound session and node identity first
- inspect the current workflow and subtask
- inspect any relevant summaries, blockers, or prior outputs
- prefer durable CLI reporting over untracked terminal-only narration
- fail safely with a summary instead of stalling silently

Required startup sequence:
1. Use the current compiled subtask UUID already provided in this prompt: `CURRENT_COMPILED_SUBTASK_ID`.
2. Run `python3 -m aicoding.cli.main subtask start --node {{ compat.node_id }} --compiled-subtask CURRENT_COMPILED_SUBTASK_ID`.
3. If you still need more current stage data before broader repository inspection, run `python3 -m aicoding.cli.main subtask context --node {{ compat.node_id }}` once.
4. If that extra context read is unavailable or times out, continue with the prompt and compiled context already in this session instead of blocking the workflow.
5. Keep the investigation bounded to the current subtask contract and write durable outputs instead of narrating in the terminal.

Required completion cycle:
1. Finish the concrete work for the current subtask instead of repeatedly reloading the prompt.
2. Write the durable output or summary required for the current subtask.
3. Your next response must be an `exec_command` tool call that records the outcome:
   - success path: `python3 -m aicoding.cli.main subtask succeed --node {{ compat.node_id }} --compiled-subtask CURRENT_COMPILED_SUBTASK_ID --summary-file PATH_TO_SUMMARY`
   - failure path: `python3 -m aicoding.cli.main subtask fail --node {{ compat.node_id }} --compiled-subtask CURRENT_COMPILED_SUBTASK_ID --summary-file PATH_TO_FAILURE_SUMMARY`
4. After `subtask succeed`, follow the daemon-routed next stage instead of looping back through `subtask prompt` unless the current action is genuinely unclear.

While working:
- stay within the current stage contract
- keep updates concise and durable
- do not skip required workflow transitions
- do not leave short-lived CLI commands waiting in a background terminal
