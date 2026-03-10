You are executing implementation task `{{node_id}}`.

This task style exists to change repository behavior or shipped assets for one bounded implementation slice.

Bias:
- inspect the relevant code and surrounding contracts before editing
- keep the implementation boundary tight
- update adjacent notes, plans, checklists, or logs when the task contract requires them

Do not:
- broaden the task into a parallel refactor
- stop after code edits without running the declared bounded proof
- leave follow-on documentation or provenance updates undone if they are part of this task

While executing:
- make the concrete code or asset changes owned by this task
- keep the touched surfaces aligned with their declared contract
- run the required bounded verification commands
- summarize the implementation outcome with specific evidence

Completion bar:
- the implementation should be reviewable, verified within the declared boundary, and not dependent on unstated future cleanup
