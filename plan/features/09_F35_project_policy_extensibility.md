# Phase F35: Project Policy Extensibility

## Goal

Allow projects to override or extend ladders, policies, hooks, quality gates, and prompt packs safely.

## Rationale

- Rationale: The design promises project-specific ladders, gates, hooks, and prompt packs, so extension has to be a supported mechanism instead of an unsafe patch point.
- Reason for existence: This phase exists to let projects adapt the orchestration system safely while preserving validation, auditability, and deterministic compilation.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`: F01 is one of the core surfaces projects may redefine.
- `plan/features/03_F04_yaml_schema_system.md`: F04 constrains how extensibility is expressed safely.
- `plan/features/10_F06_override_and_merge_resolution.md`: F06 provides the merge behavior extensibility depends on.
- `plan/features/27_F26_hook_system.md`: F26 is a key policy-controlled extension mechanism.
- `plan/features/36_F33_optional_isolated_runtime_environments.md`: F33 is one optional policy-controlled capability.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/contracts/yaml/override_conflict_semantics.md`
- `notes/contracts/runtime/runtime_environment_policy_note.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`

## Scope

- Database: persist resolved policy state where auditability requires it.
- CLI: inspect project policy, effective policy, and policy impact.
- Daemon: validate and enforce legal policy combinations.
- YAML: author project policy schemas and resolution rules.
- Prompts: controlled prompt-pack override/extension.
- Tests: exhaustive policy inheritance, override legality, and invalid-combination coverage.
- Performance: benchmark policy resolution during compile.
- Notes: update policy notes when unsafe combinations are discovered.
