You are defining child `plan` nodes for documentation sub-epic `{{node_id}}`.

This delivery band exists to align notes, plans, checklists, commands, and other authoritative docs with actual behavior or intended future behavior.

Bias:
- separate inventory, authoring, and verification work when that improves correctness
- treat documentation as a contract surface, not cleanup

Do not:
- write plans that say only "update docs"
- omit document-family consistency or command-surface checks where applicable
- assume code already proves what the docs claim

Each plan should make explicit:
- which document families are in scope
- which contradictions or gaps it addresses
- which tests or command checks prove the docs are aligned

Closure bar:
- the docs band should leave the repo more truthful, more inspectable, and less contradictory

Return JSON only:
{"status":"OK","child_count":<n>}
or
{"status":"FAIL","message":"<reason>"}
