# Task: Workflow Overhaul Profile Subtask Chain Simulations

## Goal

Add a new workflow-overhaul future-plan directory containing compiled subtask-chain simulations for every draft workflow profile.

## Rationale

- Rationale: The workflow-overhaul bundle now has profile definitions, prompt contracts, and prompt composition rules, but it still lacks a compact simulation surface that shows what compiled subtask chain each profile is actually expected to produce.
- Reason for existence: This task exists to make the draft profile behavior inspectable at the runtime-shape level before implementation starts, so profile discussions are not limited to YAML fields and prompts alone.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/45_F04_runtime_policy_and_prompt_schema_families.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_definition_schema_draft.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_prompt_contract.md`
- `plan/future_plans/workflow_overhaul/starter_workflow_profiles/README.md`
- `plan/future_plans/workflow_overhaul/rich_layout_examples/README.md`

## Scope

- Database: not directly affected.
- CLI: not directly affected beyond later inspection and simulation-read surfaces.
- Daemon: clarify the future compiled runtime shape each profile is expected to produce.
- YAML: derive the simulations from the draft profile and layout metadata rather than inventing unrelated flows.
- Prompts: align the simulated chains with the current prompt contract and prompt composition model.
- Tests: run the document-schema and task-plan verification surface after adding the new directory and required artifacts.
- Performance: keep the simulations compact and readable rather than duplicating full flow notes.
- Notes: add the new simulation directory, README, grouped profile simulation docs, and required development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- a new workflow-overhaul directory exists for compiled subtask-chain simulations
- every draft workflow profile appears in the new simulation docs
- each simulated chain shows the profile's expected compiled subtask sequence and completion gate posture
- the required development log records the reviewed files, commands run, and results
