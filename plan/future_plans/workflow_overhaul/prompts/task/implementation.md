Overlay Role Delta
- Use with `task/base.md`.
- This overlay turns the task into a bounded implementation task.
- Inspect the relevant code and surrounding contracts before editing.

Overlay Objective Delta
- Make the concrete code or asset changes owned by this task and verify them inside the declared boundary.

Additional Forbidden Actions
- Do not broaden the task into a parallel refactor.
- Do not stop after code edits without running the declared bounded proof.
- Do not leave required follow-on documentation or provenance updates undone when they belong to this task.

Profile-Specific Completion Conditions
- The implementation is reviewable.
- Required bounded proof ran or is honestly blocked.
- The task does not depend on unstated future cleanup.
