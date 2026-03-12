# Task: Workflow Overhaul Remaining Open Decisions

## Goal

Resolve the remaining workflow-overhaul future-plan questions around migration shape, `effective_layout_id` persistence, route and response posture for the new inspection surfaces, compile-context schema shape, and precedence between registered generated layouts and profile-default layouts.

## Rationale

- Rationale: The prior workflow-overhaul planning passes closed the high-level direction, but a smaller set of storage, route-shape, and layout-precedence questions still remained open and would continue to destabilize later authoritative planning if left implicit.
- Reason for existence: This task exists to capture those remaining planning decisions explicitly inside the future-plan bundle before any authoritative implementation plans are opened.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/65_F04_layout_replacement_and_hybrid_reconciliation.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_workflow_profile_persistence_and_surface_decisions.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_api_response_shapes.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_route_design.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `src/aicoding/db/models.py`
- `src/aicoding/daemon/materialization.py`

## Scope

- Database: define the intended migration posture and whether `effective_layout_id` deserves a first-class column.
- CLI: define whether the new workflow-profile inspection surfaces should stay additive or overload existing commands.
- Daemon: define route shape and layout-precedence posture against the current generated-layout registration path.
- YAML: define how compile-context should snapshot layout/profile-derived structure without overcoupling to mutable source YAML.
- Prompts: not directly affected beyond ensuring the compile-context and brief schema can carry prompt-reference metadata.
- Tests: update future notes so later authoritative slices know what route and precedence behavior they must prove.
- Performance: keep selectors cheap and richer detail in compiled payloads unless a clear indexed lookup need exists.
- Notes: update the workflow-overhaul future-plan bundle and required development log.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the future-plan bundle records explicit decisions for migration posture, `effective_layout_id`, route/response posture, compile-context shape, and generated-layout precedence
- the breakdown note reflects those decisions so they no longer read as materially open
- the required development log records the reviewed files, commands run, and results
