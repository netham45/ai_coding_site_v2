You are defining child `phase` nodes for feature epic `{{node_id}}`.

This epic style exists to deliver a feature through:
- discovery
- implementation
- documentation alignment
- real proving

Role of this tier:
- create the minimum coherent set of delivery bands needed to take a feature from request to real proof
- ensure implementation is not separated from notes, checklist, and E2E obligations

Bias:
- require explicit implementation, docs, and real-E2E coverage
- prefer a small number of strong bands over many decorative phases

Do not:
- stop at bounded proof only
- omit the documentation-alignment band
- create a phase that duplicates another phase's contract

Inputs:
- user request: `{{user_request}}`
- epic goal: `{{node.title}}`
- acceptance criteria: `{{acceptance_criteria}}`
- required child roles: `{{required_child_roles}}`
- context bundle: `{{context_bundle}}`

Expected phase roles usually include:
- discovery
- implementation
- docs
- e2e

For each phase:
- make the delivery boundary explicit
- identify expected outputs and required updates
- name verification targets that belong to that phase
- keep dependencies minimal and real

Return JSON only:
{"status":"OK","child_count":<n>,"coverage":{"missing_roles":[],"extra_roles":[]}}
or
{"status":"FAIL","message":"<reason>"}
