# Phase F35: Project Policy Extensibility

## Goal

Allow projects to override or extend ladders, policies, hooks, quality gates, and prompt packs safely.

## Scope

- Database: persist resolved policy state where auditability requires it.
- CLI: inspect project policy, effective policy, and policy impact.
- Daemon: validate and enforce legal policy combinations.
- YAML: author project policy schemas and resolution rules.
- Prompts: controlled prompt-pack override/extension.
- Tests: exhaustive policy inheritance, override legality, and invalid-combination coverage.
- Performance: benchmark policy resolution during compile.
- Notes: update policy notes when unsafe combinations are discovered.
