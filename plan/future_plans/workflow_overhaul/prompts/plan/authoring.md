You are defining child `task` nodes for authoring plan `{{node_id}}`.

This plan style exists to produce or revise authoritative written artifacts such as task plans, feature plans, notes, checklists, inventories, or contract docs.

Bias:
- keep authorship work traceable to explicit artifact families
- separate investigation, writing, and verification when that improves correctness
- make command and checklist alignment visible rather than implied

Do not:
- create generic tasks like "update docs"
- bury the authoritative files in broad prose
- treat unverified writing as complete when the plan expects schema or command checks

Each task should make explicit:
- which document or note families it edits
- which contradictions, gaps, or missing surfaces it addresses
- which verification commands or review checks prove the authored result

Closure bar:
- the plan should end with authoritative artifacts that are more truthful, more inspectable, and tied to explicit verification

Return JSON only:
{"status":"OK","child_count":<n>}
or
{"status":"FAIL","message":"<reason>"}
