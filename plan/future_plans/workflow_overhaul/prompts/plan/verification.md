You are defining child `task` nodes for verification plan `{{node_id}}`.

This plan style exists to prove that previously authored or implemented work satisfies its declared contract.

Bias:
- tie each task to a specific proving surface
- keep commands, evidence, and pass/fail interpretation explicit
- separate defect discovery from later remediation work unless the plan contract combines them

Do not:
- write tasks that say only "run tests"
- leave the canonical commands or expected evidence implicit
- claim completion without naming the contradiction or failure path if verification breaks

Each task should make explicit:
- which behavior, artifact family, or invariant it proves
- which commands, diagnostics, or inspections it runs
- what evidence or outputs it leaves behind
- what failure classification it can produce if proof does not hold

Closure bar:
- downstream operators should be able to see exactly what was proven, what was not, and what needs remediation if a task fails

Return JSON only:
{"status":"OK","child_count":<n>}
or
{"status":"FAIL","message":"<reason>"}
