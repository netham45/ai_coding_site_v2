You are generating a plan layout for node `{{node_id}}`.

Inputs:
- phase goal: `{{node.title}}`
- acceptance criteria: `{{acceptance_criteria}}`
- user request: `{{user_request}}`

Your job:
- create the minimum coherent set of `plan` children needed to deliver the phase

Requirements:
- each child must have a clear execution boundary
- dependencies must be explicit and minimal
- outputs and acceptance criteria must be concrete
- do not create children that merely restate the phase title

Output contract:
- produce a valid `layout_definition`
- keep the structure executable, reviewable, and small
