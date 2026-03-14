Overlay Role Delta
- Use with `task/base.md`.
- This overlay turns the task into a bounded remediation task.
- Tie every change back to a named finding, failed command, or contradiction.
- Every remediation task is expected to hand off directly into a follow-up verification or re-review step.

Overlay Objective Delta
- Resolve one concrete finding, contradiction, or failed proof result without losing traceability to the issue that caused the work.

Additional Forbidden Actions
- Do not fold unrelated improvement work into the remediation packet.
- Do not lose the evidence trail explaining why the task exists.
- Do not claim the issue is resolved without naming the re-check or proof surface.
- Do not finish remediation without preserving the exact reverification target that must run next.

Profile-Specific Completion Conditions
- The issue-to-change-to-proof chain is explicit.
- Re-verification was attempted honestly.
- A downstream reviewer can see what changed and how it was proven.
- The remediation result is specific enough for the daemon to route immediately into the paired reverification step.
