Recover the interrupted session for node `{{node_id}}`.

Steps:
- inspect `session show --node {{node_id}}` or `session show-current`
- follow the daemon's `recommended_action` before choosing attach vs resume
- reload the current workflow and stage context
- recover the current cursor from durable state
- restate the exact active subtask
- continue from the last durable checkpoint

Do not replay unrelated work or assume volatile terminal context is still trustworthy.
