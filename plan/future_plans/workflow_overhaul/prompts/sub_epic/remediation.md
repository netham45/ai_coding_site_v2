You are defining child `plan` nodes for remediation sub-epic `{{node_id}}`.

This delivery band exists to resolve issues found earlier without losing the traceability of why the fixes exist.

Bias:
- tie each plan back to concrete findings
- keep remediation scoped and evidence-driven
- preserve a clean handoff to re-review or verification

Do not:
- invent unrelated improvement work
- hide which findings are being addressed
- treat remediation as complete without defining the proving surface

Each plan should make explicit:
- which findings or contradictions it addresses
- what changes are expected
- what notes, checklists, or logs must be updated
- what proves the remediation is complete

Closure bar:
- every plan must leave a downstream reviewer able to see what changed and why

Return JSON only:
{"status":"OK","child_count":<n>}
or
{"status":"FAIL","message":"<reason>"}
