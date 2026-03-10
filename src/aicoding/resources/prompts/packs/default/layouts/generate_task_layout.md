You are generating a task layout for node `{{node_id}}`.

Inputs:
- plan goal: `{{node.title}}`
- acceptance criteria: `{{acceptance_criteria}}`
- user request: `{{user_request}}`

Your job:
- create the minimum coherent set of `task` children needed to implement the plan

Requirements:
- each task must have a crisp implementation goal
- acceptance criteria must be directly testable or reviewable
- avoid speculative decomposition with no execution benefit
- if one task is enough, create exactly one task

Output contract:
- produce a valid `layout_definition`
- keep each child concrete enough to execute without reinterpreting the plan
