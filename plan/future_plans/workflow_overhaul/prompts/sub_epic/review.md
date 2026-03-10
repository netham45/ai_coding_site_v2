You are defining child `plan` nodes for review sub-epic `{{node_id}}`.

This delivery band exists to inspect the current state, gather evidence, and produce actionable findings.

Bias:
- emphasize diagnosis, evidence gathering, and traceability
- keep finding categories and remediation handoff clear

Do not:
- blur review work into remediation work unless the phase contract explicitly combines them
- produce vague "check everything" plans
- lose track of which artifacts provide the evidence for a finding

Each plan should make explicit:
- what it is inspecting
- what evidence it must gather
- what finding or judgment categories it can produce
- what remediation handoff artifacts it must leave behind

Closure bar:
- review outputs must support a downstream remediation band without redoing the inspection

Return JSON only:
{"status":"OK","child_count":<n>}
or
{"status":"FAIL","message":"<reason>"}
