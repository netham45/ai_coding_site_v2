Review the generated layout against the current request.

Check:
- coverage of the request and acceptance criteria
- overlap or duplication between children
- dependency correctness
- whether the child set is smaller than necessary without becoming vague

Return a bounded pass, revise, or fail judgment with concrete fixes.

Record the judgment through the CLI:
- `python3 -m aicoding.cli.main review run --node {{node_id}} --status pass --summary "Approved the generated layout."`
- if the layout needs changes, replace `--status pass` with `--status revise`
- if the layout is unacceptable, replace `--status pass` with `--status fail`
- if useful, write structured findings to `reviews/findings.json` and structured criteria to `reviews/criteria.json`, then pass them with `--findings-file reviews/findings.json --criteria-file reviews/criteria.json`
- do not rely on prose alone; submit the review judgment with `review run`
