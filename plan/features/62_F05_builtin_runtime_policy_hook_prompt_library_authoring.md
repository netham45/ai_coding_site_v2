# Phase F05C: Built-In Runtime Policy, Hook, And Prompt Library Authoring

## Goal

Author the built-in YAML and prompt families that control runtime policy, hooks, and operational guidance.

## Rationale

- Rationale: Runtime policy, hooks, and operational prompts define how the system actually behaves in edge cases, recovery, and guidance scenarios.
- Reason for existence: This phase exists to ship the default operational control plane assets that make the built-in system coherent end to end.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/08_F05_default_yaml_library.md`: F05 is the parent feature for built-in asset authoring.
- `plan/features/09_F35_project_policy_extensibility.md`: F35 shapes how built-in policy assets are extended or overridden.
- `plan/features/27_F26_hook_system.md`: F26 consumes the built-in hook definitions authored here.
- `plan/features/43_F05_prompt_pack_authoring.md`: F05-S2 supplies the prompt library content packaged here.
- `plan/features/60_F05_builtin_node_task_layout_library_authoring.md`: F05A covers the adjacent structural built-ins that reference this operational layer.
- `plan/features/61_F05_builtin_validation_review_testing_docs_library_authoring.md`: F05B covers adjacent validation/review/testing/docs built-ins that should stay aligned.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/prompts/prompt_library_plan.md`
- `notes/catalogs/inventory/default_yaml_library_plan.md`
- `notes/catalogs/audit/yaml_builtins_checklist.md`
- `notes/contracts/yaml/hook_expansion_algorithm.md`
- `notes/contracts/runtime/runtime_environment_policy_note.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`

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
