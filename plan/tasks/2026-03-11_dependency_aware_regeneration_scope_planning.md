# Task: Dependency-Aware Regeneration Scope Planning

## Goal

Author an explicit feature plan for fixing the rebuild-scope gap where regenerating one sibling leaves dependent siblings reusable even though their effective inputs changed.

## Rationale

- Rationale: The current regeneration doctrine and implementation both treat rebuild scope as descendant-only, which is incompatible with sibling dependency semantics once regenerated prerequisite work must be reflected in dependent sibling output.
- Reason for existence: This task exists to convert that discovered gap into an authoritative implementation slice with explicit system coverage, proof requirements, and note-alignment expectations.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/11_F08_dependency_graph_and_admission_control.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/77_F08_incremental_parent_merge_phase_03_merge_backed_dependency_truth.md`
- `plan/features/78_F15_incremental_parent_merge_phase_04_dependent_child_parent_refresh.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/pseudocode/modules/regenerate_node_and_descendants.md`
- `notes/planning/implementation/regeneration_and_upstream_rectification_decisions.md`

## Scope

- Database: no schema change in this planning pass, but the feature plan must call out rebuild-event and audit implications for dependency-driven scope expansion.
- CLI: no direct CLI change in this planning pass, but the feature plan must preserve operator inspection expectations for rebuild scope, cutover-readiness, and rebuild coordination.
- Daemon: define the missing dependency-aware regeneration-scope behavior and defensive rectification guard.
- YAML: no direct YAML change in this planning pass, but the feature plan must keep the code-vs-YAML boundary explicit.
- Prompts: define the prompt-context implications without inventing a new prompt family prematurely.
- Tests: define bounded, integration, and real E2E proof for the new rebuild-scope rule.
- Performance: identify the expected closure-calculation cost and query-shape concerns.
- Notes: add the authoritative feature plan and record the planning work through the development log.

## Planned Changes

1. Add a feature plan under `plan/features/` for dependency-aware regeneration scope.
2. Clarify how that feature interacts with candidate replay ordering, required cutover scope, and existing rebuild/cutover CLI surfaces.
3. Record the planning batch in `notes/logs/features/` or adjacent authoritative doc-update logs.
4. Run the authoritative document-family tests covering the changed planning artifacts.

## Verification

Canonical verification commands for this task:

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_feature_plan_docs.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the regeneration-scope gap is captured in an authoritative feature plan
- the plan explains affected systems, replay-versus-live-merge boundaries, and proof expectations clearly enough for implementation
- the governing task plan and development log reference each other
- the documented verification commands are run and their results are recorded honestly
