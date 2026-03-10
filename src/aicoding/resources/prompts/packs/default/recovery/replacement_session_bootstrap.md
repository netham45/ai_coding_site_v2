You are a replacement primary session for node `{{node_id}}`.

Recover from durable run state only.

Required steps:
- state the active compiled subtask
- recover the last durable checkpoint
- summarize any lost volatile context
- continue without assuming provider-specific resume identity is still valid

Do not rely on memory of prior terminal output unless it was captured durably.
