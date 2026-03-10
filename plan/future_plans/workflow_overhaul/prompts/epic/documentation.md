You are defining child `phase` nodes for documentation epic `{{node_id}}`.

This epic style exists to inventory, author, verify, and repair authoritative documentation.

Role of this tier:
- define the documentation lifecycle as explicit delivery bands
- ensure authoring is separated from verification and remediation
- keep command alignment, checklist accuracy, and document-schema proving visible

Bias:
- prefer inventory, authoring, verification, and remediation bands
- treat repository notes and authoritative docs as implementation assets rather than polish

Do not:
- mix code implementation work into the core documentation bands unless it is strictly required for command or contract alignment
- skip verification and jump from authoring to completion
- hide structural document obligations in loose prose

Inputs:
- user request: `{{user_request}}`
- epic goal: `{{node.title}}`
- acceptance criteria: `{{acceptance_criteria}}`
- required child roles: `{{required_child_roles}}`
- context bundle: `{{context_bundle}}`

Expected phase roles usually include:
- inventory
- authoring
- verification
- remediation

For each phase:
- identify the document families or note families in scope
- define required outputs
- define verification targets, including document-schema tests where applicable
- define what remediation means if authoring or verification reveals contradictions

Return JSON only:
{"status":"OK","child_count":<n>,"coverage":{"missing_roles":[],"extra_roles":[]}}
or
{"status":"FAIL","message":"<reason>"}
