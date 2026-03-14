Overlay Role Delta
- Use with `plan/base.md`.
- This overlay turns the plan into a verification plan.
- Separate defect discovery from later remediation unless the plan contract combines them, and leave a deterministic remediation-plus-reverification path when findings stay inside the current plan boundary.

Overlay Objective Delta
- Produce verification tasks that prove a declared behavior or artifact surface through explicit commands and evidence.

Additional Forbidden Actions
- Do not write tasks that say only "run tests."
- Do not leave canonical commands or expected evidence implicit.
- Do not claim completion without naming contradiction or failure posture.
- Do not repair substantive implementation at the plan layer.
- Do not treat a failed proof result as terminal if the plan can still emit bounded remediation work plus a follow-up reverification step.

Profile-Specific Expected Result
- A task child set for verification work.

Profile-Specific Completion Conditions
- Each task names the behavior, artifact family, or invariant it proves.
- Commands and evidence expectations are explicit.
- Failure classifications are clear enough for downstream remediation.
- Findings that can be fixed locally have an explicit remediation and reverification route.
