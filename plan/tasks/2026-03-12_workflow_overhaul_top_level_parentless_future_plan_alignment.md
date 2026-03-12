# Task: Workflow Overhaul Top-Level Parentless Future-Plan Alignment

## Goal

Align the `plan/future_plans/workflow_overhaul/` bundle with the repository doctrine that top-ness is structural rather than semantic, and make the future intent explicit that the built-in `epic`, `phase`, `plan`, and `task` tiers should all be able to start parentless at the top level and that every draft workflow profile should be startable top-level through its own `applies_to_kind`, with planned proof coverage for that rule.

## Rationale

- Rationale: The authoritative specs and reconciliation notes already state that any node kind may be top-level when its hierarchy definition allows `allow_parentless: true`, but the workflow-overhaul future-plan bundle still reads as epic-rooted by default and risks silently reintroducing the narrower assumption.
- Reason for existence: This task exists to keep the future-plan bundle aligned with the current hierarchy doctrine, to record the intended future built-in posture that `phase`, `plan`, and `task` can also run top-level, to make explicit that draft profiles should not require an epic wrapper when their own kind is parentless-capable, and to define the intended bounded, integration, and real-E2E proving expectations before any profile-aware implementation begins.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/08_F05_default_yaml_library.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/reconcilliation/01_top_level_node_hierarchy_reconciliation.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_e2e_coverage_matrix.md`
- `plan/future_plans/workflow_overhaul/prompts/README.md`
- `plan/future_plans/workflow_overhaul/starter_workflow_profiles/README.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`

## Scope

- Database: not directly affected by this future-plan-only documentation pass.
- CLI: not directly changed, but the future-plan notes must preserve the existing expectation that top-level startup surfaces accept any hierarchy-allowed parentless kind.
- Daemon: not directly changed, but the future proving plan must still require daemon validation to derive top-level legality from hierarchy definitions rather than an epic-only special case.
- YAML: no runtime YAML changes in this task, but the future-plan notes must remain consistent with the `allow_parentless` hierarchy model and explicitly state the intended future built-in parentless set.
- Prompts: update prompt-bundle framing only as needed so epic-heavy examples are not misread as an exclusive top-level rule.
- Tests: update the future proving notes so bounded, integration, and real-E2E coverage for parentless non-epic starts and top-level profile starts across the shipped profile set is explicit.
- Performance: not directly affected by this documentation pass.
- Notes: update the workflow-overhaul future-plan documents and the required development log so the planned behavior and proof story are explicit and auditable.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the workflow-overhaul future-plan bundle explicitly states that top-ness is structural rather than semantic
- the bundle explicitly says the built-in `epic`, `phase`, `plan`, and `task` tiers are intended to be valid top-level starts in the future direction
- the bundle explicitly says draft workflow profiles should be startable top-level through their own `applies_to_kind`
- the future proving notes explicitly require bounded, integration, and real-E2E coverage for that built-in parentless and profile-startable set
- the development log cites this governing task plan and records the commands actually run
