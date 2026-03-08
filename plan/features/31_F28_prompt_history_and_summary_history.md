# Phase F28: Prompt History And Summary History

## Goal

Persist prompts, prompt-template identity, and summaries as durable audit artifacts.

## Scope

- Database: prompt history, prompt roles, summary taxonomy, prompt-template identity.
- CLI: prompt list/show and summary history commands.
- Daemon: correct prompt issuance and summary registration timing.
- YAML: clean prompt references from compiled tasks and quality gates.
- Prompts: finalize prompt-pack roles, identity, and retrieval behavior.
- Tests: exhaustive prompt lineage, summary registration, role correctness, and historical retrieval coverage.
- Performance: benchmark prompt-history queries.
- Notes: update prompt and summary taxonomy notes if needed.
