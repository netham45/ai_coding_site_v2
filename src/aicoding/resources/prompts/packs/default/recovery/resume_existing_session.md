Resume the existing primary session for node `{{node_id}}`.

Required steps:
- inspect the durable session record and confirm its `recommended_action`
- reload the current durable run state
- restate the active compiled subtask
- confirm the last durable checkpoint
- continue from there without repeating completed work
