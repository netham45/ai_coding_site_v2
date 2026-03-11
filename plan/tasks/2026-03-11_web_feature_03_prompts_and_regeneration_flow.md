# Task: Web Feature 03 Prompts And Regeneration Flow

## Goal

Implement prompt history, prompt editing, and supersede-plus-regenerate flow for the website using the existing node-versioning and regeneration semantics.

## Rationale

- Rationale: Prompt revision is one of the highest-value operator mutations and has to preserve version history rather than clobbering a node in place.
- Reason for existence: This task exists to make the browser capable of updating a node prompt, creating a new candidate version, and triggering regeneration through the same two-step daemon semantics already used elsewhere.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/03_prompts_and_regeneration_flow.md`
- `plan/features/05_F02_node_versioning_and_supersession.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/31_F28_prompt_history_and_summary_history.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`

## Scope

- Database: no schema change is planned in this slice; rely on durable node-version, prompt-history, and regeneration records.
- CLI: no CLI command changes are planned; browser behavior must stay aligned with the existing `node supersede` and `node regenerate` semantics.
- Daemon: reuse `/api/nodes/{node_id}/prompt-history`, `/api/nodes/{node_id}/supersede`, `/api/nodes/{node_id}/regenerate`, `/api/nodes/{node_id}/lineage`, and `/api/node-versions/{version_id}`.
- Website: add a prompt tab with editable prompt text, inline confirmation flow, prompt-history rendering, and post-mutation refresh behavior.
- YAML: not applicable.
- Prompts: this feature directly covers node prompt editing and delivered prompt history inspection.
- Tests: cover prompt loading, candidate-version blocking state, keep-editing, discard-changes, save-and-regenerate, and browser proof of the route-driven flow.
- Performance: refresh only the affected node and project surfaces after prompt mutations.
- Notes: record the discovered daemon invariant that regeneration reuses the latest candidate version when one already exists.

## Planned Changes

1. Add the governing task plan and development log for the prompt/regeneration slice.
2. Extend the frontend prompt API module with node-version lookup, supersede mutation, and regenerate mutation helpers.
3. Add a `prompts` detail tab that shows the editable node prompt, current version metadata, and delivered prompt history.
4. Implement the inline `save and regenerate now?` confirmation strip with `save and regenerate`, `discard changes`, and `keep editing`.
5. Block prompt supersede in the browser when the node already has a live candidate version, while still rendering the latest candidate details.
6. Extend the mock daemon with deterministic prompt-history, node-version, supersede, and regenerate behavior.
7. Add bounded frontend proof for the mutation flow and Playwright coverage for the prompt-edit narrative.
8. Update the implementation note and relevant future-plan note with the discovered latest-candidate regeneration behavior.

## Verification

Canonical verification commands for this task:

```bash
python3 -m pytest tests/integration/test_node_versioning_flow.py -q
cd frontend && npm run test:unit
cd frontend && npm run build
cd frontend && npm run test:e2e
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the website exposes a real `prompts` tab
- the prompt editor loads the current latest version prompt rather than inventing local state from nowhere
- prompt mutation uses supersede-plus-regenerate semantics and does not clobber prior versions
- the confirmation flow is inline and supports `save and regenerate`, `discard changes`, and `keep editing`
- live-candidate conflict is surfaced honestly in the browser
- prompt history is inspectable from the browser
- affected invalidation and refresh behavior is documented and tested
- the governing task plan and development log reference each other
- the documented verification commands are run and their result is recorded honestly
