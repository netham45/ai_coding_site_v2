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

- Database: persist the authoritative registered child-plan or generated-layout reference; no polling-only workspace contract is acceptable.
- CLI: add or reconcile the authoritative parent-facing command that registers a generated child plan/layout by filename.
- Daemon: ensure compiled parent workflows can pick up the scoped decomposition configuration and consume the registered child plan rather than ambient workspace files.
- YAML: introduce or document the project/override path that swaps parent ladders for this specific runtime narrative.
- Prompts: add or scope any parent prompt assets needed for the decomposition ladder used by this narrative, including the explicit register-by-filename handoff.
- Tests: add bounded proof that the scoped path resolves to the decomposition ladder while the default built-in path stays unchanged, and that parent-generated child plans are registered through the CLI rather than discovered implicitly.
- Performance: keep the scoped override path lightweight and compile-time only.
- Notes: document clearly that this is a scoped runtime profile or override, not a silent global default change, and that generated child plans require explicit CLI registration.

## Plan

### Phase 3A: Scoped decomposition configuration

1. Decide the authoritative scoping mechanism for this narrative.
2. Freeze the parent handoff contract as `generate file -> register by filename -> materialize/spawn from durable registration`.
3. Add the scoped parent ladder and any required prompt assets.
4. Keep the built-in default parent ladders unchanged unless the notes are explicitly revised.

Exit criteria:

- the automated hierarchy narrative can compile a decomposition ladder without mutating the global default path
- the parent-generated child plan/layout is not treated as implicitly authoritative until a CLI registration step occurs

### Phase 3B: Registration contract and bounded runtime surface

1. Add or reconcile the CLI command surface for registering a generated child plan/layout by filename.
2. Ensure the daemon/runtime consumes the registered durable child-plan reference rather than ambient workspace discovery.
3. Keep direct operator `node materialize-children --node <id>` available as an explicit action, but not as a hidden substitute for parent registration.

Exit criteria:

- parent decomposition has an auditable CLI handoff from generated file to durable registered child plan
- runtime child creation is driven from the registered durable source rather than a constant filesystem lookup

### Phase 3C: Bounded proof and notes

1. Add compile/flow tests for the scoped parent workflow chain.
2. Add bounded proof for the register-by-filename handoff.
3. Update notes, plan references, and logs to reflect the scoping rule.

Exit criteria:

- bounded tests prove the scoped decomposition path and the unchanged default path side by side
- bounded tests prove that parent-generated child plans become authoritative only after explicit CLI registration

## Verification

- `python3 -m pytest tests/unit/test_workflows.py tests/integration/test_workflow_compile_flow.py tests/integration/test_daemon.py -q`
- `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- A scoped parent decomposition path exists for the automated hierarchy narrative.
- Parent-generated child plans/layouts are registered explicitly through the CLI by filename before runtime child creation uses them.
- The default built-in parent ladders are not silently changed.
- Notes and logs state that scoping boundary explicitly.
