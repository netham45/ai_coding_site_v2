You are defining child `plan` nodes for sub-epic or phase `{{node_id}}`.

Role of this tier:
- break one delivery band into executable plan slices
- keep all plans inside the boundary of the current phase role
- make per-plan outputs, dependencies, and proving intent explicit

Do not:
- re-plan the whole epic
- create tasks directly unless the phase clearly collapses to one plan with one downstream task set
- create plans that differ only cosmetically
- leave verification or required updates implicit

Inputs:
- phase profile: `{{workflow_profile}}`
- phase role: `{{node_role}}`
- phase goal: `{{node.title}}`
- phase rationale: `{{node.rationale}}`
- acceptance criteria: `{{acceptance_criteria}}`
- expected outputs: `{{expected_outputs}}`
- required updates: `{{required_updates}}`
- verification targets: `{{verification_targets}}`
- relevant context: `{{context_bundle}}`

Your job:
- produce the minimum coherent set of `plan` children
- give each child one clear execution boundary
- ensure the combined plan set fully satisfies the phase

Each child must include:
- `id`
- `role`
- `workflow_profile`
- `name`
- `goal`
- `rationale`
- `artifact_targets`
- `required_updates`
- `verification_targets`
- `dependencies`
- `acceptance`
- `ordinal`

Quality bar:
- each plan must own one distinct execution slice inside the current phase
- artifact targets must name the surfaces being changed or inspected
- required updates must stay explicit rather than implied by the role name
- verification targets must be concrete enough to map into later task commands
- acceptance criteria must let a parent or operator decide whether the plan is complete

Return JSON only:
{"status":"OK","child_count":<n>}
or
{"status":"FAIL","message":"<reason>"}
