# Task: Generated Layout Materialization Runtime Phase

## Goal

Make `node materialize-children` consume a real workspace-generated child layout when one exists, instead of always reading the packaged built-in layout file.

## Rationale

- Rationale: The current runtime asks parent AI sessions to write `layouts/generated_layout.yaml`, but child materialization ignores that file today.
- Reason for existence: Without this phase, any later automated decomposition E2E would be dishonest because the parent AI output would not actually control child creation.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/20_F15_child_node_spawning.md`
- `plan/e2e_tests/02_e2e_core_orchestration_and_cli_surface.md`
- `plan/tasks/2026-03-10_automated_full_tree_cat_runtime_e2e.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/planning/implementation/builtin_node_task_layout_library_authoring_decisions.md`

## Scope

- Database: preserve current authoritative parent-child records and idempotency behavior while allowing a different authoritative layout source.
- CLI: keep `node materialize-children --node <id>` as the canonical mutation surface.
- Daemon: change materialization so it resolves the effective child layout from the workspace first, then falls back to the built-in default layout.
- YAML: keep the built-in fallback layouts intact.
- Prompts: no prompt wording change is required in this phase beyond documenting that generated layout output becomes authoritative when present.
- Tests: add bounded coverage for generated-layout preference, fallback behavior, and idempotency.
- Performance: keep layout resolution cheap and filesystem-local.
- Notes: update runtime/materialization notes to describe the new authoritative layout resolution order.

## Plan

### Phase 1A: Runtime resolution path

1. Add a daemon-owned layout resolution helper for parent materialization.
2. Prefer `layouts/generated_layout.yaml` from the active workspace when it exists.
3. Fall back to the existing built-in layout for the parent kind when no generated layout file exists.

Exit criteria:

- a real workspace-generated layout file affects the created child set

### Phase 1B: Bounded proof and notes

1. Extend materialization tests for generated-layout preference and fallback.
2. Update the relevant runtime/materialization notes and development log.

Exit criteria:

- bounded tests prove the runtime now follows the documented layout resolution order

## Verification

- `python3 -m pytest tests/unit/test_materialization.py -q`
- `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- Generated child layouts influence runtime child creation when present.
- Built-in layouts remain the fallback path.
- Notes and logs describe the real materialization behavior honestly.
