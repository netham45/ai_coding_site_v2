You are defining child `plan` nodes for discovery sub-epic `{{node_id}}`.

This delivery band exists to converge understanding before execution-heavy work begins.

Bias:
- favor research, scope clarification, risk capture, invariant definition, and handoff clarity
- produce plans that end with actionable downstream inputs rather than open-ended analysis

Do not:
- produce implementation plans unless discovery explicitly includes a bounded proof spike
- leave ambiguities unresolved if they block later bands

Each plan should answer one discovery need such as:
- repository and note investigation
- constraint and invariant clarification
- implementation boundary definition
- proof or verification mapping

Closure bar:
- downstream implementation bands should not need to rediscover core requirements or invariants

Return JSON only:
{"status":"OK","child_count":<n>}
or
{"status":"FAIL","message":"<reason>"}
