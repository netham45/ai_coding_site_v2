You are defining child `task` nodes for plan `{{node_id}}`.

Role of this tier:
- turn one concrete plan into executable work packets
- ensure every required artifact update and verification command is owned by at least one task
- keep task boundaries small enough to execute cleanly but large enough to close real work

Do not:
- re-plan the whole parent phase
- create vague tasks such as "continue implementation"
- hide note, checklist, log, or proof obligations in rationale text only
- split work with no isolation, dependency, or review benefit

Inputs:
- plan profile: `{{workflow_profile}}`
- plan goal: `{{node.title}}`
- plan rationale: `{{node.rationale}}`
- acceptance criteria: `{{acceptance_criteria}}`
- expected outputs: `{{expected_outputs}}`
- required updates: `{{required_updates}}`
- verification targets: `{{verification_targets}}`
- policy constraints: `{{policy_constraints}}`
- relevant context: `{{context_bundle}}`

Your job:
- produce the minimum coherent set of `task` children
- give each child one concrete execution boundary
- assign explicit artifact ownership and proof obligations
- keep dependencies necessary and visible

Each child must include:
- `id`
- `role`
- `workflow_profile`
- `name`
- `goal`
- `rationale`
- `artifact_targets`
- `required_updates`
- `verification_commands`
- `dependencies`
- `acceptance`
- `ordinal`

Quality bar:
- each task should be executable without reinterpretation
- verification commands must be concrete rather than gestural
- required updates must name the affected artifact families
- acceptance criteria must allow an operator or reviewer to judge completion
- the task set must collectively cover the plan's artifact targets and proof obligations

Return JSON only:
{"status":"OK","child_count":<n>}
or
{"status":"FAIL","message":"<reason>"}
