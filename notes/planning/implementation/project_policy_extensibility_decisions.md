# Project Policy Extensibility Decisions

Date: 2026-03-08
Phase: `plan/features/09_F35_project_policy_extensibility.md`

## Decisions

1. Project policy is implemented as a separate YAML family.
   Project-local policy documents now live under `yaml/project/project-policies/*.yaml` and are validated independently from built-in runtime policy definitions.

2. Effective policy merges are deterministic and shallow.
   The current implementation merges project policy over the built-in default runtime policy by:
   - overriding default scalar settings
   - appending unique runtime/hook/review/testing/docs refs
   - replacing prompt-pack selection
   - replacing enabled node kinds when explicitly declared

3. Project policy is compile-visible, not runtime-only.
   Effective policy and policy impact are embedded into compiled workflow payloads, and project policy source documents are included in source lineage so policy-driven gating is auditable.

4. Safety checks happen before compile succeeds.
   Invalid node-kind references, unsupported prompt-pack names, and broken referenced built-in assets are rejected during policy resolution rather than being silently ignored.

## Deferred Work

- full override/merge semantics for project-local document replacement
- project-defined hierarchy documents beyond enabled-kind gating
- project prompt pack authoring beyond safe root selection
- runtime enforcement of declared environment profiles
