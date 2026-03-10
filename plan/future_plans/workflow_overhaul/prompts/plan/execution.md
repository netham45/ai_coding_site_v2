You are defining child `task` nodes for execution plan `{{node_id}}`.

This plan style exists to deliver a concrete implementation slice through direct repository work.

Bias:
- produce tasks with crisp execution boundaries
- keep code, note, checklist, and bounded-proof obligations attached to the task that creates the change
- prefer a small number of substantial tasks over decorative splitting

Do not:
- create one giant "implement the whole plan" task
- split by file count alone when there is no real boundary
- push required proof or repository updates into an unspecified later task

Each task should make explicit:
- what system boundary or artifact surface it changes
- what supporting repository updates it owns
- what verification commands it must run
- what later tasks, if any, depend on its output

Closure bar:
- every execution task should leave a reviewable, bounded-proof-ready output rather than an ambiguous partial state

Return JSON only:
{"status":"OK","child_count":<n>}
or
{"status":"FAIL","message":"<reason>"}
