Overlay Role Delta
- Use with `task/base.md`.
- This overlay turns the task into a bounded verification task.
- Execute the declared checks directly rather than inferring success from adjacent signals.
- If the checks reveal a local, fixable gap, emit `needs_remediation` so the runtime can append remediation plus reverification deterministically.

Overlay Objective Delta
- Run the declared proving commands for this bounded surface and preserve their results honestly.

Additional Forbidden Actions
- Do not replace declared commands without escalation.
- Do not hide blocked or flaky proof behind a partial-success summary.
- Do not claim the surface is proven if the commands were not actually run.
- Do not collapse a fixable verification failure into generic `failed` when the declared corrective path is available.

Profile-Specific Completion Conditions
- Command results are preserved clearly.
- Environment assumptions are visible enough for downstream review.
- Remaining proof obligations are explicit if any stay open.
- Findings that stay within the current task boundary are explicit enough to drive daemon-owned remediation and follow-up reverification.
