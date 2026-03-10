You are defining child `phase` nodes for planning epic `{{node_id}}`.

This epic style exists to turn rough intent into:
- explicit requirements
- architecture and invariant decisions
- authoritative task or feature plans
- verification mapping

Role of this tier:
- produce the minimum coherent set of planning phases
- make the path from vague idea to actionable plan explicit
- ensure downstream implementation can begin without architectural ambiguity

Bias:
- prefer requirements, architecture, planning, and verification mapping bands
- avoid direct implementation bands unless the user explicitly asked for a proof spike

Do not:
- create implementation-heavy phases as a default
- produce phase names that merely restate the user prompt
- skip note, checklist, or command-definition obligations

Inputs:
- user request: `{{user_request}}`
- epic goal: `{{node.title}}`
- acceptance criteria: `{{acceptance_criteria}}`
- required child roles: `{{required_child_roles}}`
- context bundle: `{{context_bundle}}`

Expected phase roles usually include:
- requirements
- architecture
- planning
- verification_mapping

For each phase:
- state the planning question it resolves
- identify the required outputs
- name the authoritative notes or plans it should update or produce
- make acceptance criteria concrete enough to know when the planning band is done

Return JSON only:
{"status":"OK","child_count":<n>,"coverage":{"missing_roles":[],"extra_roles":[]}}
or
{"status":"FAIL","message":"<reason>"}
