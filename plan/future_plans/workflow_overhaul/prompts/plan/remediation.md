Overlay Role Delta
- Use with `plan/base.md`.
- This overlay turns the plan into a remediation plan.
- The remediation plan must preserve a concrete handoff back to verification or re-review.

Overlay Objective Delta
- Produce bounded corrective tasks that resolve named findings, contradictions, or failed proof results and leave follow-up reverification explicit.

Additional Forbidden Actions
- Do not lose the finding-to-task mapping that justified the remediation plan.
- Do not widen the plan into unrelated cleanup.
- Do not mark remediation done without naming the follow-up verification surface.
- Do not absorb parent-scope replanning work if the finding exceeds the current plan boundary.

Profile-Specific Expected Result
- A task child set for bounded remediation with explicit reverification handoff.

Profile-Specific Completion Conditions
- Each task maps back to a named finding or failed proof.
- The remediation plan includes the concrete reverification command or downstream verification target.
- Out-of-boundary findings are escalated rather than hidden inside local remediation.
