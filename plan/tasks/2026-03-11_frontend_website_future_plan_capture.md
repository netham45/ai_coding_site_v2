# Task: Capture Frontend Website Future Plan

## Goal

Capture the proposed frontend website UI idea as a repository-local future-plan bundle, preserve the exploratory planning, convert the resulting execution-ready slices into authoritative plans under `plan/web/` with setup, feature, and verification families that follow the repository document-schema rules, and update the repository doctrine so the website UI is recognized as a sixth first-class system.

## Rationale

- Rationale: The repository already expects future ideas to be recorded without overstating implementation readiness, and this frontend/UI idea needs to be captured in a way that stays aligned with the daemon-authority and operator-surface design already present in the project.
- Reason for existence: This task exists to preserve the user's original website/UI concept, add a concrete and deeply elaborated review of how it should fit the current architecture, record the initial v1 scoping decision, freeze the first-review version of the v1 surface area, identify which daemon API surfaces already exist, identify the backend gaps the website will still require, define the intended app structure and route model, define a baseline UI consistency language, clarify how the website should choose source repos from `repos/`, define the intended top-level node creation flow including explicit operator-entered title input, propose concrete request/response contracts for top-level creation and expanded tree responses, define the intended frontend communication model around a central HTTP client, describe the later top-level merge-back operator flow, replace the overly coarse three-phase delivery idea with a much more granular setup/feature/verification sequence, convert the stabilized planning slices into an authoritative `plan/web/` family with document-schema coverage, and update the repository doctrine so website work is no longer treated as outside the core system model.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`: the web UI would need to remain a daemon client rather than bypassing the live authority model.
- `plan/features/15_F11_operator_cli_and_introspection.md`: the proposed website is effectively a richer operator surface for state, history, lineage, and diagnostics.
- `plan/features/31_F28_prompt_history_and_summary_history.md`: the detailed node view explicitly depends on prompt, summary, and related history surfaces.
- `plan/features/34_F32_automation_of_all_user_visible_actions.md`: the website should only expose actions that are real, durable, and automatable through the existing command/runtime surface.
- `plan/features/48_F11_operator_structure_and_state_commands.md`: the tree, hierarchy, and state views overlap directly with this command family.
- `plan/features/49_F11_operator_history_and_artifact_commands.md`: the detailed node view also overlaps with history, artifacts, provenance, and related inspection surfaces.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/architecture/authority_and_api_model.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/planning/implementation/fastapi_dependency_and_auth_foundation_decisions.md`
- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `AGENTS.md`

## Scope

- Database: not applicable for implementation; this task does not change durable product-state schema, though the future note discusses database-backed read models the UI would need.
- CLI: not applicable for implementation; the review maps the future web UI to existing and expected CLI/operator surfaces without changing the CLI contract.
- Daemon: not applicable for implementation; the review discusses the existing FastAPI/daemon authority model and recommends how a future web client should reuse it.
- YAML: not applicable for implementation; the future note identifies possible future YAML-discoverable forms and feature metadata but does not modify active YAML assets.
- Prompts: not applicable for implementation; the companion review discusses future prompt-aware UI surfaces and HTML-form ideas without changing shipped prompts.
- Tests: run the document-schema tests for the new task plan and development log after adding the future-plan bundle.
- Performance: negligible for this task; the review note records future performance-sensitive UI concerns such as tree rendering, incremental loading, and polling.
- Notes: add and refine a non-authoritative future-plan bundle under `plan/future_plans/` with the original starting idea, a deeply expanded review/expansion note, a dedicated v1 scope-freeze note, an information-architecture note, a UI-consistency note, a top-level node creation-flow note, dedicated contract notes for top-level creation and expanded tree responses, a frontend communication/data-access note, and granular delivery-planning notes covering many setup, feature, and verification phases, including the website-side `repos/` selection model and the deferred top-level merge-back flow; convert the ready slices into authoritative `plan/web/setup/*.md`, `plan/web/features/*.md`, and `plan/web/verification/*.md` families; and update the repository doctrine notes and plan doctrine surfaces to recognize the website UI as a first-class system.

## Verification

- Document-schema coverage: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`

## Exit Criteria

- `plan/future_plans/frontend_website_ui/` exists as a new future-plan bundle.
- The bundle contains a file preserving the original starting idea.
- The bundle contains a substantially expanded companion review/expansion note grounded in current repository architecture and explicit about v1 scope.
- The bundle contains a dedicated v1 scope-freeze note with exact proposed screens, in-scope actions, deferred actions, and draft daemon response shapes for review.
- The bundle records which website data surfaces already exist in the daemon and which require backend expansion.
- The bundle contains a dedicated information-architecture and routing note.
- The bundle contains a dedicated UI-consistency and design-language note.
- The bundle contains a dedicated top-level node creation-flow note that freezes the basic v1 creation screen and records that the operator enters the top-level title explicitly.
- The bundle records the current backend-backed title-length constraint for v1 creation and defers dynamic in-browser prompt-help guidance to a later v3-style feature.
- The bundle records the current backend top-level workflow start behavior, the recommendation to expand the existing tree route rather than add a second tree route, and the recommendation to keep action legality in daemon Python logic rather than YAML policy.
- The bundle contains a dedicated top-level creation contract note, a dedicated expanded-tree contract note, and a dedicated frontend communication/data-access note that freezes the Axios-centered client direction and other frontend architectural conventions that should be decided early.
- The bundle elaborates concrete frontend propositions for API module ownership, query keys, mutation invalidation rules, Playwright `data-testid` conventions, shared loading/empty/error primitives, badge vocabulary, status-color mapping, and spacing tokens.
- The bundle contains a proposed granular delivery plan and separate future notes for setup, feature, and verification families.
- The proposed delivery notes no longer stop at three coarse phases; they now break setup, feature, and verification into many smaller phases with testing obligations at every stage.
- The feature-family planning keeps the stronger category-level feature plans as the main units while treating route/view/component coverage as nested implementation and test obligations inside those plans rather than replacing them.
- The bundle contains a final proposed implementation-plan list, a concrete v1 action table, a recommended mock-daemon/Playwright harness note, and a final verification checklist to close the remaining pre-implementation planning gaps.
- `plan/web/README.md` exists and links to the document-schema surfaces.
- `plan/web/setup/` exists with authoritative setup-family plans.
- `plan/web/features/` exists with authoritative feature-family plans.
- `plan/web/verification/` exists with authoritative verification-family plans.
- The authoritative document-family inventory and rulebook record the `plan/web` family.
- The document-schema tests cover the new `plan/web` family.
- The bundle records that website project selection should be daemon-backed and may be presented as choosing a directory under `repos/`, without imposing that same limitation on the CLI.
- The bundle records a deferred but explicit operator flow for merging a top-level parent branch back into the selected base repo.
- `AGENTS.md` recognizes the website UI as a sixth first-class system with explicit responsibilities and stack expectations.
- The adjacent authority and planning doctrine surfaces no longer speak as if only database, CLI, daemon, YAML, and prompts are first-class systems.
- `plan/future_plans/README.md` lists the new bundle.
- The governing task plan and development log exist and point to each other.
- The documented verification command passes.
