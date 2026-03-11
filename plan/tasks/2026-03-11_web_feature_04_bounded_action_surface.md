# Task: Web Feature 04 Bounded Action Surface

## Goal

Implement the bounded website action surface and daemon-derived generic action catalog for the approved v1 action set.

## Rationale

- Rationale: The website needs actionable operator controls, but action legality must come from daemon runtime state rather than ad hoc frontend rules.
- Reason for existence: This task exists to turn the approved bounded v1 actions into a coherent browser surface with explicit blocked reasons, inline confirmations, and refresh behavior.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/04_bounded_action_surface.md`
- `plan/features/34_F32_automation_of_all_user_visible_actions.md`
- `plan/features/72_F13_expanded_human_intervention_matrix.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_action_table.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`

## Scope

- Database: rely on existing durable mutation, event, and audit records.
- CLI: no CLI command changes are planned; browser actions must stay aligned with existing daemon/CLI semantics.
- Daemon: add a generic action catalog that evaluates legality from current runtime state and existing intervention/recovery/reconciliation helpers.
- Website: add an `actions` tab that renders the daemon catalog and executes the bounded v1 actions with inline confirmation.
- YAML: not applicable.
- Prompts: prompt-update remains on the prompts tab; only `regenerate_node` from the action table is in scope here.
- Tests: cover action-catalog legality, blocked reasons, at least one blocked state, and browser execution of at least one bounded action flow.
- Performance: action refresh should invalidate only the current node and current project surfaces.
- Notes: keep the implementation aligned with the v1 action table and record any narrowed first pass honestly.

## Planned Changes

1. Add the governing task plan and development log for the action-surface slice.
2. Add daemon response models and a `GET /api/nodes/{node_id}/actions` route.
3. Implement daemon-side action legality evaluation for the bounded v1 action set using existing runtime helpers.
4. Add a frontend action API module and an `actions` detail tab.
5. Wire action execution to the existing concrete daemon endpoints rather than a browser-only mutation path.
6. Extend the mock daemon with deterministic action catalog and action mutation behavior.
7. Add backend integration coverage for the action catalog and browser proof for the action tab.
8. Record the actual action-catalog design in an implementation note and update adjacent planning docs if implementation reveals a mismatch.

## Verification

Canonical verification commands for this task:

```bash
python3 -m pytest tests/integration/test_web_actions_api.py -q
cd frontend && npm run test:unit
cd frontend && npm run build
cd frontend && npm run test:e2e
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the daemon exposes a generic node action catalog
- action legality and blocked reasons are daemon-derived
- the website exposes an `actions` tab that renders real action rows
- at least the approved bounded v1 actions are represented honestly, even if some are blocked in the current state
- browser-side execution uses the existing concrete daemon endpoints
- refresh behavior is targeted and documented
- the governing task plan and development log reference each other
- the documented verification commands are run and their result is recorded honestly
