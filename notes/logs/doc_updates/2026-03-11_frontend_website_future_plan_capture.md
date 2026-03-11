# Development Log: Capture Frontend Website Future Plan

## Entry 1

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: started
- Affected systems: notes, plans, development logs
- Summary: Started a documentation-only task to preserve a future browser-based operator UI idea, record the original braindump, and review it against the current daemon/API and operator-surface architecture.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/README.md`
  - `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`
  - `plan/features/15_F11_operator_cli_and_introspection.md`
  - `plan/features/34_F32_automation_of_all_user_visible_actions.md`
  - `notes/specs/architecture/authority_and_api_model.md`
  - `notes/specs/cli/cli_surface_spec_v2.md`
  - `notes/planning/implementation/fastapi_dependency_and_auth_foundation_decisions.md`
  - `notes/catalogs/checklists/authoritative_document_family_inventory.md`
  - `notes/catalogs/checklists/document_schema_rulebook.md`
  - `notes/catalogs/checklists/document_schema_test_policy.md`
  - `AGENTS.md`
- Commands and tests run:
  - `rg --files plan notes`
  - `rg -n "future_plans|Task Plan|task plan|plan/tasks" -S .`
  - `sed -n '1,220p' plan/future_plans/README.md`
  - `sed -n '1,260p' plan/tasks/README.md`
  - `sed -n '1093,1165p' AGENTS.md`
  - `sed -n '1,260p' tests/unit/test_document_schema_docs.py`
  - `sed -n '1,260p' tests/unit/test_task_plan_docs.py`
  - `sed -n '1,220p' plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`
  - `sed -n '1,220p' plan/features/15_F11_operator_cli_and_introspection.md`
  - `sed -n '1,220p' plan/features/34_F32_automation_of_all_user_visible_actions.md`
  - `sed -n '1,220p' notes/specs/architecture/authority_and_api_model.md`
  - `sed -n '1,220p' notes/planning/implementation/fastapi_dependency_and_auth_foundation_decisions.md`
  - `sed -n '1,220p' notes/specs/cli/cli_surface_spec_v2.md`
- Result: Confirmed that `plan/future_plans/` is a non-authoritative working-notes family, that meaningful doc work still needs a governing task plan and development log, and that the browser-UI idea should be reviewed through the daemon-authority and operator-surface contracts.
- Next step: Add the frontend future-plan bundle, preserve the original starting idea, add the review/expansion note, and run the document-schema tests for the authoritative task-plan and log surfaces.

## Entry 2

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Added a new `plan/future_plans/frontend_website_ui/` working-notes bundle, preserved the original starting idea in its own file, added a companion review-and-expansion note tied to the current daemon/API architecture, and updated the relevant plan indexes.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/README.md`
  - `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`
  - `plan/features/15_F11_operator_cli_and_introspection.md`
  - `plan/features/34_F32_automation_of_all_user_visible_actions.md`
  - `notes/specs/architecture/authority_and_api_model.md`
  - `notes/specs/cli/cli_surface_spec_v2.md`
  - `notes/planning/implementation/fastapi_dependency_and_auth_foundation_decisions.md`
  - `notes/catalogs/checklists/authoritative_document_family_inventory.md`
  - `notes/catalogs/checklists/document_schema_rulebook.md`
  - `notes/catalogs/checklists/document_schema_test_policy.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Passed. The frontend UI idea now has a preserved original note plus a grounded critique/expansion note, and the authoritative task-plan and development-log surfaces remain valid.
- Next step: If the UI moves toward implementation, split it into authoritative tasks for daemon browser read models, action-catalog APIs, auth/routing behavior, frontend app scaffolding, and Playwright E2E coverage.

## Entry 3

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Reopened the same future-plan task for a deeper planning pass after the user requested a much more extensively elaborated note structure and agreed to drop full CLI parity as a v1 requirement.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `sed -n '1,260p' plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `sed -n '1,320p' plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `sed -n '1,260p' notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
- Result: Scope for the note bundle was expanded from a concise critique to a much more deeply structured architecture-and-roadmap exploration, with an explicit v1 scoping statement.
- Next step: Expand the review note substantially, update the governing task plan wording to reflect the deeper pass, and rerun the authoritative document tests.

## Entry 4

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Reworked the frontend website review note into a much denser architecture, scope, API, UI-model, testing, invariants, and roadmap exploration; updated the governing task plan to reflect the deeper pass and the explicit v1 non-parity decision.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Passed. The future-plan bundle now contains a substantially expanded review note with explicit subsections across product intent, v1 scope, information architecture, data and API models, action strategy, performance, auth, testing, invariants, and roadmap structure.
- Next step: If you want to continue planning, the next strong move is to author one more future note that freezes the exact v1 feature list and the first browser-oriented daemon response shapes.

## Entry 5

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Reopened the same frontend future-plan task to produce a concrete v1 scope-freeze artifact after the user requested exact review material rather than more open-ended expansion.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `sed -n '1,260p' plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `sed -n '1,260p' notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `sed -n '1,260p' plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
- Result: Established that the next useful artifact is a dedicated v1 scope-freeze note covering exact screens, actions, deferrals, and draft browser-oriented daemon response shapes.
- Next step: Add the v1 scope-freeze note, update the governing task plan wording, and rerun the document-schema tests.

## Entry 6

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Added a dedicated frontend website v1 scope-freeze note that fixes the proposed v1 screens, required data surfaces, in-scope actions, explicit deferrals, interaction rules, and draft daemon response shapes for review; updated the governing task plan to reflect the new artifact.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Passed. The future-plan bundle now includes a concrete v1 review artifact that is specific enough to approve, revise, or reject section by section.
- Next step: Review the exact v1 screens, in-scope actions, deferred actions, and draft response shapes; after that, split the accepted scope into authoritative daemon-read-model, action-catalog, frontend-shell, and Playwright planning tasks.

## Entry 7

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Corrected the v1 scope-freeze note after the user clarified that prompt modification must be part of v1 because regeneration is not useful without the ability to update the node prompt first.
- Plans and notes consulted:
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Pending at the start of this correction pass. The scope note and broader review note were updated to move node-level prompt update into v1 and to treat it as coupled to regeneration.
- Next step: Finish the correction pass, confirm the document tests still pass, and record the updated completion state.

## Entry 8

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Finalized the v1 scope correction so node-level prompt update is now explicitly part of v1, both in the scope-freeze note and in the broader review note, with regeneration described as a coupled operator flow rather than a standalone action.
- Plans and notes consulted:
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Passed. The scope-freeze note now includes prompt update in v1, adds the required prompt-tab and read-model support for it, updates the action catalog example, and removes broad prompt replacement from the deferred-v1 list while still deferring wider prompt-pack management.
- Next step: Review whether the v1 prompt-update UX should be a simple edit-and-save action plus separate regenerate, or a more guided two-step flow that leads directly into regeneration.

## Entry 9

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Refined the v1 prompt-edit decision after the user clarified that saving a prompt change should lead directly into regeneration confirmation, and added an explicit later-version note for saved prompt drafts.
- Plans and notes consulted:
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Pending at the start of this refinement pass. The scope note and review note were updated to specify a guided save-then-regenerate interaction and to defer saved prompt drafts to v2 or v3.
- Next step: Confirm the document tests still pass and record the updated completion state.

## Entry 10

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Finalized the prompt-edit UX clarification so v1 now describes a guided save-then-regenerate confirmation flow, and added an explicit later-version planning note for saved prompt drafts.
- Plans and notes consulted:
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Passed. The scope freeze now explicitly says prompt update should lead directly into regeneration confirmation, and saved prompt drafts are recorded as a separate later feature targeted for v2 or v3.
- Next step: Review whether the exact confirmation UX should stay as a minimal binary choice or whether v1 also needs a third option such as "save without regenerating" despite the current narrower direction.

## Entry 11

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Corrected the prompt-edit interaction order after the user clarified that save should only happen after regeneration confirmation, not before it.
- Plans and notes consulted:
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Pending at the start of this correction pass. The notes were updated so the prompt change remains unsaved until the operator confirms save-and-regenerate.
- Next step: Confirm the document tests still pass and record the corrected completion state.

## Entry 12

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Finalized the prompt-edit interaction ordering so v1 now clearly says prompt edits stay unsaved until the operator confirms the save-and-regenerate action.
- Plans and notes consulted:
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Passed. The notes now reflect the intended UX ordering: edit prompt, confirm save-and-regenerate, then save plus regenerate only if confirmed.
- Next step: Continue v1 review against the remaining scope-freeze questions, or split the accepted scope into authoritative follow-on planning tasks.

## Entry 13

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Reopened the future-plan bundle to reconcile it against the actual current daemon API after reviewing the implemented routes and response models. This pass changes the notes from "invent browser payloads" toward "reuse what exists and explicitly list the real backend gaps."
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/README.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_original_starting_idea.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `src/aicoding/daemon/app.py`
  - `src/aicoding/daemon/models.py`
  - `AGENTS.md`
- Commands and tests run:
  - `rg -n "@app\\.(get|post|patch|put|delete)|response_model=" src/aicoding/daemon/app.py -S`
  - `sed -n '1128,1410p' src/aicoding/daemon/app.py`
  - `sed -n '1768,1908p' src/aicoding/daemon/app.py`
  - `sed -n '2191,2490p' src/aicoding/daemon/app.py`
  - `rg -n "class (TreeCatalogResponse|TreeNodeResponse|NodeOperatorSummaryResponse|PromptHistoryCatalogResponse|SummaryHistoryCatalogResponse|CompiledWorkflowResponse|RunProgressResponse|RegenerationResponse)" src/aicoding/daemon/models.py -A20 -B3`
- Result: Confirmed that most of the website's read surface already exists, while project selection, richer tree rollups and timestamps, generic action catalogs, and some prompt-update legality metadata remain real backend gaps.
- Next step: Update all frontend future-plan notes to reflect daemon-surface reuse, record the concrete backend gaps, and rerun the document-schema tests.

## Entry 14

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Updated the entire frontend future-plan bundle to reflect the current daemon API reality: most of the read surface already exists, prompt update plus regenerate is treated as a two-step backend flow, and the remaining backend work is now called out explicitly as a smaller set of concrete gaps.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/README.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_original_starting_idea.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `src/aicoding/daemon/app.py`
  - `src/aicoding/daemon/models.py`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Passed. The future-plan notes now explicitly distinguish between daemon responses the website can reuse and the narrower backend gaps that still need implementation work.
- Next step: Review the backend-gap list and, if accepted, split the website work into authoritative follow-on planning tasks for project selection, richer tree payloads, action catalogs, and frontend implementation.

## Entry 15

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Expanded the future-plan bundle again to start defining the website's structural shape rather than only its scope: app shell, routes, breadcrumb rules, component families, and UI consistency expectations now need dedicated notes.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/README.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `find plan/future_plans/frontend_website_ui -maxdepth 1 -type f | sort`
  - `sed -n '1,420p' plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `sed -n '1,420p' plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- Result: Determined that the bundle needed two additional working notes: one for information architecture and routing, and one for UI consistency and design language.
- Next step: Add those notes, update the bundle indexes and governing artifacts, and rerun the document-schema tests.

## Entry 16

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Added two new frontend future notes covering information architecture/routing and UI consistency/design language, then updated the bundle README, governing task plan, and development log to reflect the added planning scope.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/README.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_ui_consistency_and_design_language.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Passed. The frontend future-plan bundle now includes dedicated notes for routing, breadcrumbs, component taxonomy, and UI consistency rules, so the website plan is no longer underspecified at the structural and design-language level.
- Next step: Review the proposed route structure, breadcrumb rules, component taxonomy, and design-language rules; after that, split accepted pieces into authoritative implementation-planning tasks.

## Entry 17

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Added an explicit v2 frontend idea for launching a code-server or in-browser VS Code session rooted at a selected node's working directory, and threaded that idea through the scope, routing, and design-language notes.
- Plans and notes consulted:
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_ui_consistency_and_design_language.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Pending at the start of this refinement pass. The future-plan bundle now records node-scoped browser editor access as an explicit post-v1 feature instead of an untracked idea.
- Next step: Confirm the document-schema tests still pass and keep the editor idea in the deferred website roadmap.

## Entry 18

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Finalized the v2 editor-surface addition so the frontend website plan now explicitly tracks node-scoped code-server / in-browser VS Code access as a deferred later feature across the scope, routing, and design-language notes.
- Plans and notes consulted:
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_ui_consistency_and_design_language.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Passed. The frontend bundle now treats browser-hosted editor access as an explicit v2 candidate rather than a stray untracked idea.
- Next step: Continue reviewing the website plan, or start splitting the accepted v1 and v2 ideas into separate authoritative planning tasks when you are ready.

## Entry 19

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Incorporated another round of user decisions and reconciled them against current backend behavior, including repo-list-based project selection, root-node auto-selection, debug-toggle JSON visibility, inline prompt confirmation, and the fact that top-level workflow creation does not currently clone a repo.
- Plans and notes consulted:
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_ui_consistency_and_design_language.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `src/aicoding/daemon/workflow_start.py`
  - `src/aicoding/daemon/app.py`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `sed -n '1,260p' src/aicoding/daemon/workflow_start.py`
  - `sed -n '1668,1735p' src/aicoding/daemon/app.py`
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Pending at the start of this pass. The notes were updated to freeze more product decisions and to call out the mismatch between repo-backed project expectations and the present top-level workflow-start behavior.
- Next step: Confirm the document tests still pass and record the updated completion state.

## Entry 20

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Finalized another frontend plan-freeze pass: project selection is now documented as a daemon-managed configured repo list, project routes now default to the root node, raw JSON is positioned behind debug toggles, prompt confirmation is positioned inline rather than modal-first, and the current mismatch between repo-backed project expectations and existing top-level workflow-start behavior is documented explicitly.
- Plans and notes consulted:
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_ui_consistency_and_design_language.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `src/aicoding/daemon/workflow_start.py`
  - `src/aicoding/daemon/app.py`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Passed. The website future-plan bundle now captures these product decisions and the backend constraint that top-level workflow start does not presently clone a repo.
- Next step: Review the one remaining substantive product decision about which exact prompt-changing backend mutation path should be considered canonical for the website, then split the accepted scope into authoritative planning tasks.

## Entry 21

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Froze the remaining prompt-update backend decision for the website: prompt update plus regeneration should reuse the current version/supersede semantics so the outcome is a new node version and the original remains inspectable rather than being clobbered in place.
- Plans and notes consulted:
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Pending at the start of this final decision-freeze pass. The frontend notes were updated to make node-version supersession the canonical website path for prompt update plus regeneration.
- Next step: Confirm the document tests still pass and then treat the website prompt-update semantics as frozen for future planning.

## Entry 22

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Finalized the last major prompt-update planning decision for the website: prompt edit plus regeneration should reuse the current version/supersede semantics so the action yields a new node version and preserves prior versions for inspection and lineage.
- Plans and notes consulted:
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Passed. The website future-plan bundle now treats version-preserving supersession as the canonical prompt-update path instead of leaving that behavior ambiguous.
- Next step: With that decision frozen, the frontend future-plan bundle is ready to be split into authoritative implementation-planning tasks when you want to move from future planning into execution.

## Entry 23

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Reopened the frontend future-plan bundle to correct the git-workflow framing, make the website-side project picker explicitly daemon-backed from directories under `repos/`, and add a deferred but explicit UI flow for merging a top-level parent branch back into the selected base repo.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
  - `src/aicoding/daemon/live_git.py`
  - `src/aicoding/daemon/workflow_start.py`
  - `plan/features/12_F17_deterministic_branch_model.md`
  - `plan/features/71_F11_live_git_merge_and_finalize_execution.md`
  - `notes/planning/implementation/live_git_merge_and_finalize_execution_decisions.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `sed -n '1,260p' plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `sed -n '1,260p' plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `sed -n '1,260p' plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
  - `rg -n "clone|branch|merge|seed|final" src/aicoding/daemon/live_git.py plan/features/12_F17_deterministic_branch_model.md plan/features/71_F11_live_git_merge_and_finalize_execution.md notes/planning/implementation/live_git_merge_and_finalize_execution_decisions.md`
  - `sed -n '1,260p' src/aicoding/daemon/workflow_start.py`
- Result: Pending at the start of this clarification pass. The existing child clone-and-merge-up model is now understood to already align with the intended git workflow, while the top-level source-repo bootstrap and later merge-back flow still need explicit planning.
- Next step: Finish updating the future-plan notes and governing task artifacts, rerun the document tests, and record the completed state.

## Entry 24

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Finalized the git-workflow clarification pass. The frontend notes now explicitly say the website should select projects from daemon-exposed directories under `repos/`, clarify that this is a website UX choice rather than a CLI limitation, state that all richer tree fields are required if the schema is expanded, and add a deferred but explicit operator flow for merging a top-level parent branch back into the selected base repo.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Passed. The frontend future-plan bundle now describes the current git model more accurately: child clone-and-merge-up semantics already exist in live git, while top-level source-repo bootstrap and top-level merge-back remain explicit planned work.
- Next step: If planning continues, the next strong move is to split the accepted v1 website scope and the deferred repo-bootstrap/merge-back work into separate authoritative implementation task plans.

## Entry 25

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Reopened the future-plan bundle to add a concrete phased delivery proposal for the website effort, split into setup, feature implementation, and end-to-end testing/hardening, with explicit expectations that all features land with tests and that Playwright scenarios run against controlled daemon-presented mock environments.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/README.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `ls -1 plan/future_plans/frontend_website_ui`
  - `sed -n '1,220p' plan/future_plans/frontend_website_ui/README.md`
  - `sed -n '1,220p' plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
- Result: Pending at the start of this planning pass. The missing artifact is a concrete phase breakdown that makes the website effort reviewable as setup, feature, and E2E work instead of one undivided implementation blob.
- Next step: Add the phased delivery notes, update the bundle index and governing task plan, rerun the document tests, and record the completed state.

## Entry 26

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Added a phased delivery plan plus separate future notes for setup/scaffold, feature implementation, and E2E testing/hardening. The setup note covers Node/Vite/React, Playwright, a hello-world browser test, daemon dev/proxy fit, and feature skeleton expectations. The feature note defines bounded implementation slices and states that every feature must land with tests. The E2E note defines Playwright flow families and a mock-daemon environment strategy where the daemon presents controlled API scenarios over HTTP.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/README.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phased_delivery_plan.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_1_setup_and_scaffold.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_2_feature_implementation.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_3_e2e_testing_and_hardening.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Pending at the start of this completion entry. The future-plan bundle now has an explicit proposed delivery split rather than leaving implementation batching implicit.
- Next step: Confirm the document tests pass and use these phase notes as the basis for future authoritative implementation task plans when the website effort is opened.

## Entry 27

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Reopened the future-plan bundle to add a dedicated top-level node creation-flow note after clarifying the intended v1 creation screen. This pass freezes that the operator should enter the top-level node title explicitly rather than relying on the daemon to derive it from the prompt.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_2_feature_implementation.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_3_e2e_testing_and_hardening.md`
  - `plan/future_plans/frontend_website_ui/README.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `rg -n "top-level|create node|project selector|prompt update|title" plan/future_plans/frontend_website_ui`
  - `tail -n 120 notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `sed -n '1,220p' plan/future_plans/frontend_website_ui/README.md`
- Result: Pending at the start of this planning pass. The future-plan bundle needed a dedicated top-level creation-flow artifact instead of leaving node creation implied across the broader website notes.
- Next step: Add the new note, update the affected scope and phase notes, rerun the document tests, and record the completion state.

## Entry 28

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Added a dedicated top-level node creation-flow note and threaded it through the scope and phase notes. The website plan now explicitly says the v1 creation screen should include project selection, top-level kind selection, title input, prompt input, and an inline `create node` / `keep editing` confirmation, with the title entered explicitly by the operator.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_2_feature_implementation.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_3_e2e_testing_and_hardening.md`
  - `plan/future_plans/frontend_website_ui/README.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Pending at the start of this completion entry. The website future-plan bundle now contains an explicit creation-flow note rather than leaving the top-level node creation UX underspecified.
- Next step: Confirm the document tests pass and use this creation-flow note as part of the eventual authoritative implementation planning for the website.

## Entry 29

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Reopened the future-plan bundle for another clarification pass after reviewing the current backend constraints. This pass freezes that top-level creation confirmation should require project, kind, title, and prompt to all be present; records the current `String(255)` title constraint from the database schema; and adds a deferred v3 note for dynamic in-browser prompt help aligned with future workflow-overhaul work.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `src/aicoding/db/models.py`
  - `src/aicoding/daemon/models.py`
  - `src/aicoding/daemon/workflow_start.py`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `rg -n "title = mapped_column|prompt = mapped_column|class HierarchyNode|String\\(|Text\\(" src/aicoding/db/models.py src/aicoding/daemon/manual_tree.py src/aicoding/daemon/hierarchy.py`
  - `sed -n '96,125p' src/aicoding/db/models.py`
  - `sed -n '140,240p' src/aicoding/db/models.py`
  - `sed -n '1,220p' src/aicoding/daemon/workflow_start.py`
  - `sed -n '1,220p' plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
- Result: Pending at the start of this clarification pass. The plan needed to stop treating title-length and prompt-minimum decisions as abstract when the current backend schema already constrains some of them.
- Next step: Finish the note updates, rerun the document tests, and record the completed state.

## Entry 30

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Finalized the latest clarification pass. The future-plan bundle now records that v1 creation confirmation requires project, kind, title, and prompt to all be present; that the current backend title storage is 255 characters unless migrated; and that richer in-browser prompt guidance is a deferred v3 feature tied to future dynamic workflow/tool awareness.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Pending at the start of this completion entry. The website future-plan bundle now captures these resolved validation and deferral decisions instead of leaving them as open planning questions.
- Next step: Use these frozen assumptions when the website implementation task plans are opened.

## Entry 31

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Reopened the frontend website future-plan bundle to incorporate another backend-research pass. This pass documents the current `/api/workflows/start` sequence, freezes the recommendation to expand the existing tree route rather than adding a second tree route, and elaborates the action-catalog plan into a daemon-Python rubric rather than a YAML legality map.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_2_feature_implementation.md`
  - `src/aicoding/daemon/workflow_start.py`
  - `src/aicoding/daemon/operator_views.py`
  - `src/aicoding/daemon/interventions.py`
  - `src/aicoding/daemon/models.py`
  - `src/aicoding/db/models.py`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `rg -n "class .*Tree|Tree.*Response|Action|available action|legal|legality|intervention|workflow start|start_top_level|create.*node|prompt-history|summary-history|audit|tree\\(" src/aicoding/daemon src/aicoding`
  - `sed -n '1660,1860p' src/aicoding/daemon/app.py`
  - `sed -n '1,220p' src/aicoding/daemon/workflow_start.py`
  - `sed -n '1,240p' src/aicoding/daemon/operator_views.py`
  - `sed -n '240,380p' src/aicoding/daemon/models.py`
  - `sed -n '560,700p' src/aicoding/daemon/models.py`
  - `sed -n '1,240p' src/aicoding/daemon/interventions.py`
  - `sed -n '96,125p' src/aicoding/db/models.py`
  - `sed -n '140,240p' src/aicoding/db/models.py`
- Result: Pending at the start of this research-alignment pass. The remaining work was to convert abstract planning uncertainty into concrete recommendations tied to the current daemon implementation.
- Next step: Finish note updates, rerun the document tests, and record the finalized state.

## Entry 32

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Finalized the backend-research alignment pass. The future-plan bundle now documents the existing top-level workflow-start sequence, records that v1 title constraints follow the current 255-character backend schema unless migrated, recommends expanding the existing tree route for richer browser fields, and elaborates the action-catalog plan into a daemon-side action rubric modeled after the current intervention catalog rather than a YAML policy map.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_2_feature_implementation.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Pending at the start of this completion entry. The frontend future-plan bundle now reflects these backend-driven findings rather than leaving them as open questions.
- Next step: Use these frozen response-shape and action-rubric recommendations when the authoritative website implementation task plans are created.

## Entry 33

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Reopened the frontend website future-plan bundle to turn the latest recommendations into dedicated artifacts. This pass adds a proposed top-level creation request/response contract, a proposed expanded tree-response contract, and a frontend communication/data-access note that freezes the Axios-centered client direction and related frontend architectural decisions that should be defined before implementation.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/README.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_information_architecture_and_routing.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_ui_consistency_and_design_language.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `ls -1 plan/future_plans/frontend_website_ui`
  - `sed -n '1,220p' plan/future_plans/frontend_website_ui/README.md`
  - `tail -n 120 notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
- Result: Pending at the start of this planning pass. The remaining gap was that these recommendations existed in conversation and scattered notes, but not yet as dedicated contract/convention artifacts.
- Next step: Add the three new future notes, update the task artifacts, rerun the document tests, and record the completed state.

## Entry 34

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Added three dedicated future notes: one for the proposed project-scoped top-level creation contract, one for the proposed expanded tree contract, and one for frontend communication/data access. The communication note freezes Axios as the central HTTP client direction and records other frontend conventions that should be defined early, including API module boundaries, shared query/invalidation strategy, polling rules, stable test-id conventions, and loading/empty/error patterns.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/README.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_expanded_tree_contract.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Pending at the start of this completion entry. The frontend future-plan bundle now contains dedicated contract and frontend-communication artifacts rather than leaving those decisions implied.
- Next step: Use these notes as the starting point when you open authoritative implementation planning for the website effort.

## Entry 35

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Reopened the frontend website future-plan bundle to turn the communication and design categories into concrete frontend propositions. This pass adds explicit API-module ownership recommendations, query-key shapes, mutation invalidation rules, Playwright `data-testid` naming conventions, shared loading/empty/error primitives, badge vocabulary, color-role mapping, and spacing tokens.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_ui_consistency_and_design_language.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `sed -n '1,260p' plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`
  - `sed -n '1,260p' plan/future_plans/frontend_website_ui/2026-03-11_ui_consistency_and_design_language.md`
  - `tail -n 80 notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
- Result: Pending at the start of this refinement pass. The remaining gap was that the frontend conventions were named but not yet concretely proposed.
- Next step: Finish the note updates, rerun the document tests, and record the completed state.

## Entry 36

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Finalized the frontend-conventions expansion pass. The communication and design notes now contain concrete propositions for API module boundaries, query keys, mutation invalidation, polling cadence, test-id naming, loading/empty/error primitives, badge vocabulary, semantic color mapping, and spacing-token usage.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_ui_consistency_and_design_language.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Pending at the start of this completion entry. The website future-plan bundle now gives explicit frontend architectural propositions instead of just naming categories that still needed definition.
- Next step: Use these propositions to scope the eventual frontend scaffold and first implementation batch.

## Entry 37

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Reopened the frontend website future-plan bundle to reconcile the proposed phase plans with the many newer contract and frontend-architecture decisions added afterward. This pass updates the setup, feature, E2E, and overall phased-delivery notes so they explicitly reference the central Axios/query foundation, the top-level creation and expanded-tree contracts, shared state primitives, stable test-id conventions, and the refined invalidation/testing expectations.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phased_delivery_plan.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_1_setup_and_scaffold.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_2_feature_implementation.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_3_e2e_testing_and_hardening.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_expanded_tree_contract.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_ui_consistency_and_design_language.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `sed -n '1,260p' plan/future_plans/frontend_website_ui/2026-03-11_phased_delivery_plan.md`
  - `sed -n '1,260p' plan/future_plans/frontend_website_ui/2026-03-11_phase_1_setup_and_scaffold.md`
  - `sed -n '1,280p' plan/future_plans/frontend_website_ui/2026-03-11_phase_2_feature_implementation.md`
  - `sed -n '1,280p' plan/future_plans/frontend_website_ui/2026-03-11_phase_3_e2e_testing_and_hardening.md`
- Result: Pending at the start of this reconciliation pass. The proposed phase notes needed to stop lagging behind the newer planning artifacts.
- Next step: Finish updating the phase notes, rerun the document tests, and record the completed state.

## Entry 38

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Finalized the phase-plan reconciliation pass. The phased delivery, setup, feature, and E2E notes now explicitly incorporate the central Axios/query foundation, feature API modules, shared loading/empty/error and badge primitives, the top-level creation and expanded-tree contracts, invalidation rules, and stable `data-testid` expectations.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phased_delivery_plan.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_1_setup_and_scaffold.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_2_feature_implementation.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_3_e2e_testing_and_hardening.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Pending at the start of this completion entry. The proposed implementation phases now match the current future-plan bundle rather than an earlier snapshot of it.
- Next step: Use these updated phased notes as the working split when the authoritative website implementation task plans are created.

## Entry 39

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Reopened the future-plan bundle again after the user rejected the remaining three-phase framing as still too coarse. This pass rewrites the delivery split into a much finer-grained sequence with many setup phases, many feature phases, and a final verification family that explicitly audits for missing tests and untested flows.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phased_delivery_plan.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_1_setup_and_scaffold.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_2_feature_implementation.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_3_e2e_testing_and_hardening.md`
  - `plan/future_plans/frontend_website_ui/README.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `sed -n '1,260p' plan/future_plans/frontend_website_ui/2026-03-11_phased_delivery_plan.md`
  - `ls -1 plan/future_plans/frontend_website_ui`
  - `tail -n 80 notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
- Result: Pending at the start of this rewrite pass. The remaining issue was that the planning language still implied three oversized phases instead of the route/view/component-by-component execution model the user wants.
- Next step: Finish rewriting the phase notes and supporting task artifacts, rerun the document tests, and record the completed state.

## Entry 40

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Finalized the delivery-plan rewrite. The future-plan bundle now treats the old setup/feature/E2E notes as phase families and replaces the simplistic three-phase story with a granular sequence that includes separate setup subphases, many route/view/component implementation phases, and a final verification family that explicitly audits for missing tests and untested flows.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/README.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phased_delivery_plan.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_1_setup_and_scaffold.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_2_feature_implementation.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_3_e2e_testing_and_hardening.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Pending at the start of this completion entry. The delivery split now better matches the intended "test every setup step, every route, every component family, and then explicitly audit for missing proof" bar.
- Next step: Use this granular sequence rather than the old three-phase framing when splitting the website effort into authoritative implementation task plans.

## Entry 41

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Reopened the future-plan bundle once more to correct an over-literal planning split. This pass restores the stronger original feature categories as the actual proposed feature-plan units and reframes the more granular route/view/component work as nested coverage expectations inside those plans instead of as replacements for them.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_2_feature_implementation.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phased_delivery_plan.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `sed -n '1,260p' plan/future_plans/frontend_website_ui/2026-03-11_phase_2_feature_implementation.md`
  - `sed -n '1,260p' plan/future_plans/frontend_website_ui/2026-03-11_phased_delivery_plan.md`
- Result: Pending at the start of this correction pass. The remaining issue was that the feature-family note had drifted into treating every lower-level surface as if it should be its own primary feature plan.
- Next step: Finish correcting the feature-plan structure, rerun the document tests, and record the completed state.

## Entry 42

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Finalized the feature-plan structure correction. The website planning now keeps the stronger category-level feature plans as the main proposed units, while explicitly requiring route/view/component-level implementation and testing coverage inside each of those plans.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phase_2_feature_implementation.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_phased_delivery_plan.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Pending at the start of this completion entry. The feature-planning note now better matches the intended level of granularity: strong plan units, with detailed coverage expectations nested underneath.
- Next step: Use these corrected feature-plan units rather than one-plan-per-component when splitting the website effort into authoritative implementation tasks.

## Entry 43

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Reopened the future-plan bundle for one more pre-implementation planning pass. This pass adds the last missing future notes: a final proposed implementation-plan list, a concrete v1 action table, a recommended mock-daemon/Playwright harness note, and a final verification checklist covering missing-test and untested-flow audit expectations.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/README.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `ls -1 plan/future_plans/frontend_website_ui`
  - `sed -n '1,240p' plan/future_plans/frontend_website_ui/README.md`
  - `tail -n 100 notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
- Result: Pending at the start of this final planning pass. The remaining work was to close the last obvious pre-implementation gaps before the website effort can be split into authoritative execution plans.
- Next step: Add the new future notes, update the task artifacts, rerun the document tests, and record the completed state.

## Entry 44

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Added the final pre-implementation planning notes for the frontend website bundle: a final proposed implementation-plan list, a concrete v1 action table, a recommended deterministic mock-daemon/Playwright harness note, and a final verification checklist. The future-plan bundle now has explicit answers for the remaining "what exactly do we plan to open, how do actions map to backend surfaces, how do browser tests boot scenarios, and how do we verify no important flow remains untested?" questions.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/future_plans/frontend_website_ui/README.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_final_proposed_implementation_plan_list.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_action_table.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_mock_daemon_and_playwright_harness.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_final_verification_checklist.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Pending at the start of this completion entry. The frontend future-plan bundle now covers nearly all of the planning surface needed before opening authoritative implementation tasks.
- Next step: Use these final notes to split the website work into authoritative task plans when you are ready to begin implementation.

## Entry 45

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: notes, plans, development logs
- Summary: Reopened the task to convert the finalized website planning into an authoritative `plan/web/` family. This pass creates `plan/web/setup`, `plan/web/features`, and `plan/web/verification`, maps the future-plan conclusions into those new plan files, and updates the document-schema inventory, rulebook, and tests so the new family is enforced rather than informal.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`
  - `plan/e2e_tests/06_e2e_feature_matrix.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_final_proposed_implementation_plan_list.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_action_table.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_mock_daemon_and_playwright_harness.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_final_verification_checklist.md`
  - `notes/catalogs/checklists/authoritative_document_family_inventory.md`
  - `notes/catalogs/checklists/document_schema_rulebook.md`
  - `tests/unit/test_document_schema_docs.py`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `find plan -maxdepth 2 -type d | sort`
  - `sed -n '1,240p' plan/setup/README.md`
  - `sed -n '1,240p' plan/tasks/README.md`
  - `sed -n '1,260p' notes/catalogs/checklists/authoritative_document_family_inventory.md`
  - `sed -n '1,280p' notes/catalogs/checklists/document_schema_rulebook.md`
  - `sed -n '1,260p' tests/unit/test_document_schema_docs.py`
- Result: Pending at the start of this authoritative-family adoption pass. The remaining work was to convert website planning into a first-class authoritative planning family without violating the repository’s schema/testing rules.
- Next step: Finish creating the `plan/web` files, update the schema docs/tests, rerun the document tests, and record the completed state.

## Entry 46

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: notes, plans, development logs
- Summary: Added the authoritative `plan/web` family with setup, feature, and verification subfamilies, created the first web plans from the future-plan bundle, and updated the document-schema inventory, rulebook, and tests to cover the new family. The website effort now has both exploratory future notes and authoritative execution-planning surfaces.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `plan/web/README.md`
  - `plan/web/setup/README.md`
  - `plan/web/features/README.md`
  - `plan/web/verification/README.md`
  - `notes/catalogs/checklists/authoritative_document_family_inventory.md`
  - `notes/catalogs/checklists/document_schema_rulebook.md`
  - `tests/unit/test_document_schema_docs.py`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Pending at the start of this completion entry. The repository now has an authoritative web-planning family instead of only future-plan notes for the website effort.
- Next step: Review the new `plan/web` family and decide whether any of those plans should be split further before implementation begins.

## Entry 47

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: changed_plan
- Affected systems: website, notes, plans, development logs
- Summary: Reopened the website planning task to update the repository doctrine itself. This pass promotes the website UI from future-direction language into the active doctrine by updating `AGENTS.md`, the daemon authority note, and adjacent planning doctrine files that still hard-coded the old five-system model.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
  - `notes/specs/architecture/authority_and_api_model.md`
  - `plan/features/README.md`
  - `plan/e2e_tests/00_e2e_feature_generation_strategy.md`
  - `plan/update_tests/00_raise_existing_tests_to_doctrine_level.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
- Commands and tests run:
  - `rg -n "five required systems|five systems|Which of the five systems|database, CLI, daemon, YAML, prompts|website|web ui|frontend" AGENTS.md notes plan -S`
  - `sed -n '1,260p' AGENTS.md`
  - `sed -n '1,220p' notes/specs/architecture/authority_and_api_model.md`
  - `sed -n '1,220p' plan/features/README.md`
  - `sed -n '1,220p' plan/e2e_tests/00_e2e_feature_generation_strategy.md`
  - `sed -n '1,260p' plan/update_tests/00_raise_existing_tests_to_doctrine_level.md`
- Result: Pending at the start of this doctrine-adoption pass. The remaining drift was that the repo’s core doctrine and adjacent planning doctrine still described only database, CLI, daemon, YAML, and prompts as first-class systems.
- Next step: Finish patching the doctrine files, rerun the document tests, and record the completed doctrine update.

## Entry 48

- Timestamp: 2026-03-11
- Task ID: frontend_website_future_plan_capture
- Task title: Capture frontend website future plan
- Status: complete
- Affected systems: website, notes, plans, development logs
- Summary: Updated the repository doctrine to include the website UI as a sixth first-class system. `AGENTS.md` now defines website responsibilities and stack expectations, the authority/API note now treats the website as an explicit daemon client using the repo’s bearer-token posture, the planning doctrine files now require website consideration where applicable, and the future-plan bundle no longer says doctrine adoption is still pending.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
  - `notes/specs/architecture/authority_and_api_model.md`
  - `plan/features/README.md`
  - `plan/e2e_tests/00_e2e_feature_generation_strategy.md`
  - `plan/update_tests/00_raise_existing_tests_to_doctrine_level.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
  - `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
  - `notes/logs/doc_updates/2026-03-11_frontend_website_future_plan_capture.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result: Pending at the start of this completion entry. The repo doctrine now recognizes the website as a first-class implementation system instead of leaving it only in future-planning language.
- Next step: Use the updated doctrine when opening the first real web implementation task plans and associated checklists.
