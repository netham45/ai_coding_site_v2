# Phase F05C: Built-In Runtime Policy, Hook, And Prompt Library Authoring

## Goal

Author the built-in YAML and prompt families that control runtime policy, hooks, and operational guidance.

## Scope

- Database: persist built-in identity and prompt lineage metadata where needed for inspection and reproducibility.
- CLI: expose commands to inspect runtime policy, hook, and prompt-pack built-ins.
- Daemon: load runtime policy and hook built-ins deterministically and surface prompt-pack resolution clearly.
- YAML: author built-in runtime policy definitions, hook definitions, prompt pack metadata, and operational guidance bindings.
- Prompts: author the default prompt library for decomposition, execution, error handling, missed-step detection, idle nudges, pause/resume, recovery, and operator escalation.
- Tests: exhaustively test schema validity, compileability, placeholder coverage, prompt binding integrity, and hook/policy resolution behavior.
- Performance: benchmark prompt-pack loading and policy-resolution overhead during compilation and runtime startup.
- Notes: keep prompt-library and runtime-policy notes synchronized with the authored built-ins.

## Exit Criteria

- runtime policies, hooks, and prompt packs are authored as first-class built-ins and fully covered by tests.
