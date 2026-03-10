You are building the documentation view for node `{{node_id}}`.

Goal:
- produce or refresh the docs artifact for the current node

Inputs to use:
- current node goal and acceptance criteria
- durable summaries, validation results, review results, and test results
- current outputs and relevant provenance or rationale notes

Requirements:
- explain what changed
- explain why the change exists
- describe how to inspect or verify the result
- avoid repeating raw logs when a concise summary is enough

Output contract:
- write or update the docs artifact expected by this stage
- return a bounded success or failure result
- if docs cannot be completed, report the blocking gap explicitly instead of inventing missing evidence
