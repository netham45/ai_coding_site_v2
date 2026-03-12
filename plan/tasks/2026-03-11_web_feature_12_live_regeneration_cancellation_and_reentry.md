# Task: Web Feature 12 Live Regeneration Cancellation And Reentry

## Goal

Make active-node regeneration usable by teaching the daemon to cancel conflicting live subtree state before supersede and regenerate operations continue.

## Rationale

- Rationale: The website currently fails during active-node prompt edits because supersede hard-stops on active runs and regenerate still treats live subtree state as an unconditional conflict.
- Reason for existence: This task exists to align live browser regeneration with the documented operator expectation that in-progress target and descendant work is cancelled and then rebuilt.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/12_live_regeneration_cancellation_and_reentry.md`
- `plan/web/features/03_prompts_and_regeneration_flow.md`
- `plan/web/features/04_bounded_action_surface.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_action_table.md`
- `notes/planning/implementation/frontend_website_prompts_regeneration_decisions.md`
- `notes/planning/implementation/live_rebuild_cutover_coordination_decisions.md`

## Scope

- Database: reuse durable run, session, rebuild-event, and supersession records while recording the cancellation scope honestly.
- CLI: keep regenerate semantics aligned with daemon behavior so browser and direct daemon callers do not disagree.
- Daemon: resolve cancelable subtree blockers before regenerate and optionally before supersede when the caller explicitly requests cancel-and-reenter semantics.
- Website: send the explicit cancel-before-supersede signal for prompt edits and reflect the new cancel-and-regenerate action semantics.
- YAML: not applicable.
- Prompts: preserve latest-version editing while allowing save-and-regenerate for active nodes.
- Tests: cover daemon cancellation of active subtree blockers, successful live regenerate, prompt save-and-regenerate on active nodes, and browser proof for the corrected flow.
- Performance: keep subtree blocker inspection targeted to the affected root and descendants.
- Notes: update prompt/regeneration and rebuild-coordination notes to record the new live-runtime behavior.

## Planned Changes

1. Add the task plan and development log for feature 12.
2. Add daemon-owned subtree live-state cancellation helpers that:
   - cancel active or paused runs in scope
   - invalidate active sessions tied to those runs
   - record rebuild coordination evidence for the cancellation
3. Make `POST /api/nodes/{node_id}/regenerate` clear cancelable live subtree blockers before rebuilding.
4. Extend supersede requests with an explicit cancel-active-subtree option and use it from the browser prompt flow.
5. Update mock/browser proof and notes so they reflect the corrected active-node regeneration semantics.

## Verification

Canonical verification commands for this task:

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_regeneration.py tests/integration/test_node_versioning_flow.py -q
cd frontend && npm run test:unit
cd frontend && npm run build
cd frontend && npx playwright test tests/e2e/smoke.spec.js
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- active-node regenerate no longer fails just because the authoritative subtree is running or paused
- descendant runs and active sessions in the regenerate scope are cancelled durably before rebuild proceeds
- prompt save-and-regenerate can supersede an active node when the browser explicitly requests cancel-and-reenter behavior
- daemon and browser proof cover the corrected live-regeneration behavior honestly
- the governing task plan and development log reference each other
- the documented verification commands are run and their result is recorded honestly
