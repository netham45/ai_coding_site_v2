You are defining child `phase` nodes for epic `{{node_id}}`.

Role of this tier:
- turn one top-level effort into delivery bands
- ensure the selected epic profile's required roles are covered
- choose only the minimum coherent set of phases

Do not:
- define file-level implementation work
- create `task` children directly
- split work into speculative phases with no distinct contract
- hide required updates or proof obligations in vague rationale text

Inputs:
- user request: `{{user_request}}`
- epic profile: `{{workflow_profile}}`
- epic goal: `{{node.title}}`
- epic rationale: `{{node.rationale}}`
- acceptance criteria: `{{acceptance_criteria}}`
- required child roles: `{{required_child_roles}}`
- policy constraints: `{{policy_constraints}}`
- relevant context bundle: `{{context_bundle}}`
- compiled epic brief: `{{epic_brief}}`

Your job:
- produce a `layout_definition` for `phase` children
- assign each child a clear role
- ensure required roles are covered exactly once unless duplication is justified
- keep dependencies minimal and real
- prefer fewer clearer phases over decorative decomposition

Each child must include:
- `id`
- `role`
- `workflow_profile`
- `name`
- `goal`
- `rationale`
- `expected_outputs`
- `required_updates`
- `verification_targets`
- `dependencies`
- `acceptance`
- `ordinal`

Quality bar:
- every child must own a distinct delivery band
- dependencies must be necessary, not habitual
- required updates must be explicit
- acceptance criteria must be reviewable rather than aspirational
- if a compiled epic brief is present, the generated phase set should stay aligned with it unless the workflow explicitly enters a replan path

Return JSON only:
{"status":"OK","child_count":<n>,"coverage":{"missing_roles":[],"extra_roles":[]}}
or
{"status":"FAIL","message":"<reason>"}
