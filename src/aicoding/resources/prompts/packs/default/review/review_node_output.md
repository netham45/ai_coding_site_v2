Review the current node output against its requirements, acceptance criteria, and available evidence.

Check:
- whether the expected artifact or behavior exists
- whether the evidence actually supports the claim of completion
- whether important risks or omissions remain

Return a clear pass, revise, or fail judgment with concrete reasons and the smallest next correction.

Record the judgment through the CLI:
- `python3 -m aicoding.cli.main review run --node {{node_id}} --status pass --summary "Approved the current node output."`
- if the output needs changes, replace `--status pass` with `--status revise`
- if the output fails review, replace `--status pass` with `--status fail`
- if useful, write structured findings to `reviews/findings.json` and structured criteria to `reviews/criteria.json`, then pass them with `--findings-file reviews/findings.json --criteria-file reviews/criteria.json`
- do not rely on prose alone; submit the review judgment with `review run`
