# Task: Workflow Overhaul Tier Enforcement And Prompt Guards

## Goal

Make the workflow-overhaul future-plan bundle explicit about how non-leaf tiers are prevented from claiming completion without decomposition and how higher tiers are kept out of child-owned implementation work except for narrow merge and documentation reconciliation.

## Rationale

- Rationale: The current workflow-overhaul drafts describe profile structure, prompt stacks, and completion restrictions, but the enforcement ladder between prompt guidance, compiler-frozen workflow context, and daemon legality checks is still too implicit.
- Reason for existence: This task exists to turn that implicit behavior into explicit future-plan contracts before later authoritative implementation slices encode the wrong boundary.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_definition_schema_draft.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_workflow_profile_persistence_and_surface_decisions.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
- `plan/future_plans/workflow_overhaul/prompts/README.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`

## Scope

- Database: not directly affected beyond clarifying future runtime gates that will need durable state inspection.
- CLI: clarify future inspection surfaces that expose decomposition obligations and blocked completion reasons.
- Daemon: define the code-owned legality checks for decomposition-required tiers, completion gating, and narrow merge/documentation exceptions.
- YAML: clarify that profiles declare obligations but do not own legality by themselves.
- Prompts: tighten higher-tier prompt guards so non-leaf tiers create or reconcile child work instead of performing child-owned implementation.
- Tests: update future-plan docs so later authoritative slices know what bounded tests and real E2E proof must exist for the enforcement ladder.
- Performance: keep the future enforcement posture biased toward cheap legality checks and explicit blocked reasons rather than expensive ad hoc recomputation at mutation time.
- Notes: update the workflow-overhaul future-plan bundle and required development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the workflow-overhaul notes describe the enforcement ladder across prompt, compile, daemon, CLI/UI, and verification surfaces
- non-leaf starter profiles forbid `complete`, `flow_complete`, and `release_ready` until their decomposition obligations are met
- the planning-stage prompts for epic, phase, and plan tiers explicitly prohibit child-owned implementation except for narrow merge or documentation reconciliation
- the required development log records the reviewed files, commands run, and results
