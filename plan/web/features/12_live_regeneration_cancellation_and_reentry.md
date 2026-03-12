# Web Feature 12: Live Regeneration Cancellation And Reentry

## Goal

Make browser regeneration usable when the target subtree is active by introducing daemon-owned cancel-and-regenerate orchestration and aligning prompt-edit flows with reusable candidate semantics.

## Rationale

- Rationale: The current website exposes `regenerate_node`, but the daemon blocks regeneration whenever the authoritative subtree has active or paused runtime state, and the prompts tab hard-blocks editing when a live candidate already exists.
- Reason for existence: This feature exists to convert regeneration from a mostly-blocked surface into an operator flow that can safely cancel conflicting live work, supersede the right scope, and re-enter regeneration with durable auditability.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/03_prompts_and_regeneration_flow.md`
- `plan/web/features/04_bounded_action_surface.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_action_table.md`
- `notes/planning/implementation/live_rebuild_cutover_coordination_decisions.md`
- `AGENTS.md`

## Scope

- Database: rely on durable lifecycle, session, rebuild-event, and supersession records; extend audit records only if cancel-and-regenerate needs stronger correlation across cancelled runs and rebuilt candidates.
- CLI: keep regenerate legality and runtime side effects aligned with daemon-owned semantics so browser and CLI do not disagree on what regeneration means.
- Daemon: add an explicit cancel-and-regenerate path or equivalent orchestration that cancels the in-progress or paused authoritative run for the target subtree, resolves active child runtime conflicts, and then starts regeneration safely.
- Website: expose the legality, scope, and confirmation language for cancel-and-regenerate; stop treating any existing live candidate as an unconditional prompt-edit blocker if the daemon can reuse or replace it safely.
- YAML: not applicable.
- Prompts: align prompt editing with reusable-candidate semantics and save-and-regenerate behavior.
- Tests: cover blocked regeneration, cancel-and-regenerate success, descendant cancellation scope, prompt-edit reentry when a candidate exists, and durable post-action inspection.
- Performance: cancellation polling and post-regenerate refresh should stay targeted to the affected subtree.
- Notes: update rebuild-coordination and website action notes so they state the new live-runtime semantics honestly.

## Planned Work

1. Define the daemon-owned operator contract for active-subtree regeneration:
   - inspect blockers
   - enumerate affected nodes/runs/sessions
   - confirm cancellation scope
   - cancel target and descendant live work
   - trigger regeneration
   - return durable inspection references
2. Decide whether this should land as:
   - a new combined endpoint
   - or an action-catalog mutation with daemon-owned orchestration behind it
3. Update action legality so the browser can distinguish:
   - plain regenerate
   - cancel-and-regenerate
   - hard-blocked states that still require manual intervention
4. Update prompt-edit behavior so an existing candidate can be reused or superseded according to daemon policy rather than being blocked unconditionally in the browser.
5. Add browser confirmation copy that names the subtree cancellation scope explicitly.
6. Add real E2E proof that starts with an active node, triggers regeneration from the browser-owned surface, proves cancellation of the active subtree, and proves the resulting rebuild records and refreshed UI state.

## Notes

- The current rebuild-coordination note explicitly says automatic pause/cancel flows are deferred; this phase is the corrective implementation plan for that deferred gap.
- This work must be audited carefully because it changes live runtime behavior, not just website presentation.
