Review the generated layout against the current request.

Check:
- coverage of the request and acceptance criteria
- overlap or duplication between children
- dependency correctness
- whether the child set is smaller than necessary without becoming vague
- whether the layout introduced diagnosis, discovery, reproduction, or verification-only children even though the current request already names the concrete file/module target and exact validation command
- whether the layout preserved an ancestor dependency/count narrative that the current direct request no longer requires

Revise the layout instead of passing it when:
- a concrete file-plus-test request was split into separate diagnosis/discovery and implementation children without an explicit request for that split
- the child count or dependency shape is larger than necessary for the current direct request

Return a bounded pass, revise, or fail judgment with concrete fixes.

Record the judgment through the CLI:
- `python3 -m aicoding.cli.main review run --node {{node_id}} --status pass --summary "Approved the generated layout."`
- if the layout needs changes, replace `--status pass` with `--status revise`
- if the layout is unacceptable, replace `--status pass` with `--status fail`
- if useful, write structured findings to `reviews/findings.json` and structured criteria to `reviews/criteria.json`, then pass them with `--findings-file reviews/findings.json --criteria-file reviews/criteria.json`
- do not rely on prose alone; submit the review judgment with `review run`
