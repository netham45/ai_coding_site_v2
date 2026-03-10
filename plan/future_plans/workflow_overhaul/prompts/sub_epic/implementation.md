You are defining child `plan` nodes for implementation sub-epic `{{node_id}}`.

This delivery band exists to ship the code and bounded proof for a declared implementation scope.

Bias:
- produce plans with crisp execution boundaries
- make artifact targets explicit
- ensure notes, checklist, and development-log obligations remain visible where the phase requires them

Do not:
- create broad plans such as "implement everything"
- push proving or documentation obligations into an unspecified later band if they belong here
- split by file count alone when there is no real execution boundary

Each plan should make explicit:
- what system boundary it changes
- what artifacts are expected
- what bounded tests or diagnostics it must run
- what later bands depend on its output

Closure bar:
- implementation outputs must be reviewable and bounded-proof-ready for downstream docs or E2E bands

Return JSON only:
{"status":"OK","child_count":<n>}
or
{"status":"FAIL","message":"<reason>"}
