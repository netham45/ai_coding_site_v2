You are defining child `phase` nodes for review epic `{{node_id}}`.

This epic style exists to inspect an existing system, identify issues, remediate them, and confirm the remediation.

Role of this tier:
- define the review lifecycle as explicit delivery bands
- separate inspection from remediation and re-review
- keep evidence gathering and closure visible

Bias:
- prefer inspection, evidence, remediation, and confirmation bands
- prioritize auditability and operator clarity over speculative redesign

Do not:
- collapse review and remediation into one vague band without a clear reason
- create implementation phases that are disconnected from discovered issues
- allow findings to disappear into summary prose without structured remediation

Inputs:
- user request: `{{user_request}}`
- epic goal: `{{node.title}}`
- acceptance criteria: `{{acceptance_criteria}}`
- required child roles: `{{required_child_roles}}`
- context bundle: `{{context_bundle}}`

Expected phase roles usually include:
- scope_freeze
- review
- remediation
- re_review

For each phase:
- define what evidence it must gather or consume
- define which repository artifacts it must update
- define what counts as closure for that band

Return JSON only:
{"status":"OK","child_count":<n>,"coverage":{"missing_roles":[],"extra_roles":[]}}
or
{"status":"FAIL","message":"<reason>"}
