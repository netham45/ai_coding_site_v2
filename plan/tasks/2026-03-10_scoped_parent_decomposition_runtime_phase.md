# Task: Scoped Parent Decomposition Runtime Phase

## Goal

Enable an AI-driven parent decomposition ladder for the automated full-tree runtime narrative without silently changing the global default parent ladders for all workflows.

## Rationale

- Rationale: The built-in default `epic`, `phase`, and `plan` ladders are intentionally still the leaf-like chain.
- Reason for existence: The automated full-tree `cat` narrative needs parent nodes that actually run `generate_child_layout` and `spawn_children`, but that behavior must stay scoped so the repository does not drift by surprise from the documented default posture.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`
- `plan/tasks/2026-03-10_automated_full_tree_cat_runtime_e2e.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/planning/implementation/builtin_node_task_layout_library_authoring_decisions.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/contracts/yaml/override_conflict_semantics.md`

## Scope

- Database: no new schema should be required.
- CLI: the existing workflow and inspection commands remain the canonical runtime path.
- Daemon: ensure compiled parent workflows can pick up the scoped decomposition configuration.
- YAML: introduce or document the project/override path that swaps parent ladders for this specific runtime narrative.
- Prompts: add or scope any parent prompt assets needed for the decomposition ladder used by this narrative.
- Tests: add bounded compilation proof that the scoped path resolves to the decomposition ladder while the default built-in path stays unchanged.
- Performance: keep the scoped override path lightweight and compile-time only.
- Notes: document clearly that this is a scoped runtime profile or override, not a silent global default change.

## Plan

### Phase 3A: Scoped decomposition configuration

1. Decide the authoritative scoping mechanism for this narrative.
2. Add the scoped parent ladder and any required prompt assets.
3. Keep the built-in default parent ladders unchanged unless the notes are explicitly revised.

Exit criteria:

- the automated hierarchy narrative can compile a decomposition ladder without mutating the global default path

### Phase 3B: Bounded proof and notes

1. Add compile/flow tests for the scoped parent workflow chain.
2. Update notes, plan references, and logs to reflect the scoping rule.

Exit criteria:

- bounded tests prove the scoped decomposition path and the unchanged default path side by side

## Verification

- `python3 -m pytest tests/unit/test_workflows.py tests/integration/test_workflow_compile_flow.py -q`
- `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- A scoped parent decomposition path exists for the automated hierarchy narrative.
- The default built-in parent ladders are not silently changed.
- Notes and logs state that scoping boundary explicitly.
