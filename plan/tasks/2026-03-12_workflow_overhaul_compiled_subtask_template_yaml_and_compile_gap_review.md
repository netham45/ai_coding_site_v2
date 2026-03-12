# Task: Workflow Overhaul Compiled Subtask Template YAML And Compile Gap Review

## Goal

Reflect the simulated compiled subtask chains in the workflow-overhaul draft YAML and inspect how the current runtime actually compiles and materializes subtasks.

## Rationale

- Rationale: The workflow-overhaul bundle had profile simulations in prose, but the starter profile YAML still stopped at child-generation policy and did not encode the expected compiled chain.
- Reason for existence: This task exists to unify the future-plan YAML surface with the simulation docs and to document the current compile/materialization reality before implementation work tries to bridge the gap.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/45_F04_runtime_policy_and_prompt_schema_families.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_definition_schema_draft.md`
- `plan/future_plans/workflow_overhaul/compiled_subtask_chain_simulations/README.md`
- `plan/future_plans/workflow_overhaul/compiled_subtask_chain_simulations/epic_profiles.md`
- `plan/future_plans/workflow_overhaul/compiled_subtask_chain_simulations/phase_profiles.md`
- `plan/future_plans/workflow_overhaul/compiled_subtask_chain_simulations/plan_profiles.md`
- `plan/future_plans/workflow_overhaul/compiled_subtask_chain_simulations/task_profiles.md`

## Scope

- Database: not directly affected.
- CLI: inspect the current command surface used for child materialization and merge.
- Daemon: inspect the current compile and materialization path to identify how subtasks are really assembled today.
- YAML: extend the draft starter workflow profiles with explicit compiled subtask templates.
- Prompts: not directly changed, but the new YAML should remain aligned with the prompt-contract model.
- Tests: run the task-plan and document-schema verification surface after the draft-YAML updates.
- Performance: not directly affected beyond keeping the draft compiled-chain representation compact and inspectable.
- Notes: update the workflow-profile schema draft and starter-profile README, and add the required development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- every starter workflow profile YAML includes an explicit `compiled_subtask_template`
- the schema draft documents the `compiled_subtask_template` section
- the starter profile README explains the YAML-to-simulation alignment
- the required development log records the inspection commands and doc-test result
- the current compile/materialization path is summarized clearly enough to compare against the target model
