You are generating a phase layout for node `{{node_id}}`.

Inputs:
- user request: `{{user_request}}`
- node goal: `{{node.title}}`
- acceptance criteria: `{{acceptance_criteria}}`

Your job:
- create the minimum coherent set of `phase` children needed to satisfy the request

Requirements:
- each child must own a distinct slice of work
- dependencies must reflect real ordering constraints only
- avoid speculative or overlapping children
- prefer fewer, clearer phases over unnecessary fragmentation

Output contract:
- produce a valid `layout_definition`
- keep titles, rationale, and acceptance criteria concrete and reviewable
