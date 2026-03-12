Overlay Role Delta
- Use with `task/base.md`.
- This overlay turns the task into a bounded verification task.
- Execute the declared checks directly rather than inferring success from adjacent signals.

Overlay Objective Delta
- Run the declared proving commands for this bounded surface and preserve their results honestly.

Additional Forbidden Actions
- Do not replace declared commands without escalation.
- Do not hide blocked or flaky proof behind a partial-success summary.
- Do not claim the surface is proven if the commands were not actually run.

Profile-Specific Completion Conditions
- Command results are preserved clearly.
- Environment assumptions are visible enough for downstream review.
- Remaining proof obligations are explicit if any stay open.
