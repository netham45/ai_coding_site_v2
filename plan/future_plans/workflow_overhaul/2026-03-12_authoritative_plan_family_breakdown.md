# Workflow Overhaul Authoritative Plan Family Breakdown

## Purpose

Decompose the current workflow-overhaul future-plan bundle into the set of authoritative plan slices it would likely need before real implementation begins.

This is still a future-plan artifact.

It is not an implementation claim and not yet an authoritative plan family.

## Why This Note Exists

The current bundle under `plan/future_plans/workflow_overhaul/draft/` contains:

- useful design direction
- draft prompts
- draft starter profile YAML
- draft route/model/schema notes
- a draft E2E proof matrix

But it does not yet exist in the repository's normal implementation-ready shape.

What is still missing is a repo-grounded decomposition that says, for each future slice:

- which real code files are affected
- which contracts are missing and must be authored first
- which implementation subtasks would actually be required
- which tests and verification commands would be needed
- which dependencies and blockers exist between slices

This note provides that bridge.

Follow-on future-plan decisions recorded after this breakdown now also live in:

- `plan/future_plans/workflow_overhaul/2026-03-12_workflow_profile_persistence_and_surface_decisions.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_startup_and_create_contract.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_web_ui_integration_plan.md`

## Review Basis

This breakdown was reviewed against the current implementation surfaces, including:

- `src/aicoding/yaml_schemas.py`
- `src/aicoding/hierarchy.py`
- `src/aicoding/daemon/workflow_start.py`
- `src/aicoding/daemon/workflows.py`
- `src/aicoding/daemon/materialization.py`
- `src/aicoding/daemon/app.py`
- `src/aicoding/daemon/models.py`
- `src/aicoding/cli/parser.py`
- `src/aicoding/cli/handlers.py`
- `tests/unit/test_workflow_start.py`
- `tests/unit/test_materialization.py`
- `tests/integration/test_workflow_start_flow.py`
- `tests/e2e/test_flow_01_create_top_level_node_real.py`

## Current Code Reality Summary

The current implementation already has enough stable structure to support a real authoritative breakdown:

- node kinds are YAML-driven through `src/aicoding/hierarchy.py`
- top-level startup is daemon-owned through `src/aicoding/daemon/workflow_start.py`
- workflow compilation is centralized in `src/aicoding/daemon/workflows.py`
- child materialization is centralized in `src/aicoding/daemon/materialization.py`
- CLI and API surfaces are already explicit and test-backed

The current implementation does not yet have workflow-profile support in the real runtime:

- no `workflow_profile_definition` family exists in `src/aicoding/yaml_schemas.py`
- no profile fields exist on `NodeDefinition` in `src/aicoding/hierarchy.py`
- no profile selection or profile persistence exists in `WorkflowStartRequest` or `NodeCreateRequest`
- no `node types`, `node profiles`, `workflow brief`, or `/api/workflow-profiles` surfaces exist
- materialization is still driven by the resolved layout for the parent kind, not by selected profile
- compile context does not yet freeze selected profile, child-role obligations, or generated brief content

That means the workflow-overhaul bundle should eventually become a multi-slice authoritative plan family, not one large implementation note.

## Recommended Future Plan Family

The future authoritative plan family should probably be opened as six main slices plus one sequencing/reconciliation umbrella.

Website implication:

- the eventual authoritative family should explicitly include website-facing work tied to the existing frontend future-plan bundle rather than treating browser impact as a later documentation follow-up

### Slice A: Workflow Profile YAML Family And Structural Validation

Primary goal:

- adopt `workflow_profile_definition` as a real YAML family and make the structural library understand it

Current real code surfaces:

- `src/aicoding/yaml_schemas.py`
- `src/aicoding/hierarchy.py`
- `src/aicoding/structural_library.py`
- `src/aicoding/resources/yaml/builtin/system-yaml/`

Missing contracts that should be authored first:

- authoritative `workflow_profile_definition` schema contract
- authoritative extension rules for `node_definition`
- authoritative extension rules for `layout_definition`
- authoritative built-in library validation contract for cross-references between node kinds, profiles, and layouts

Implementation subtasks that should appear in a real plan checklist:

- add a real `WorkflowProfileDefinitionDocument` model to `src/aicoding/yaml_schemas.py`
- register the new family in `FAMILY_MODELS`
- extend `NodeDefinition` with `default_workflow_profile` and `supported_workflow_profiles`
- extend `LayoutDefinitionDocument` and `LayoutChildDefinition` with profile-aware fields only after their contracts are frozen
- teach structural-library validation to load and validate `workflow_profiles/*.yaml`
- add built-in cross-reference validation between profile ids, node kinds, and layout ids
- add or revise packaged built-in YAML assets under `src/aicoding/resources/yaml/builtin/system-yaml/`

Tests and proof needed:

- unit tests for schema validation
- unit tests for structural-library cross-reference validation
- document consistency tests for any new authoritative note/checklist family adopted alongside the slice

Main dependencies:

- none; this is the likely first implementation slice

Main risk:

- adopting draft profile fields into YAML before the runtime ownership boundaries are frozen could push enforcement logic into YAML accidentally

### Slice B: Profile-Aware Startup, Creation, And Parentless Top-Level Policy

Primary goal:

- extend startup and creation surfaces so nodes can be created with a selected workflow profile and so top-level starts follow the hierarchy-driven parentless rule instead of an epic-first assumption

Current real code surfaces:

- `src/aicoding/daemon/workflow_start.py`
- `src/aicoding/daemon/manual_tree.py`
- `src/aicoding/daemon/app.py`
- `src/aicoding/daemon/models.py`
- `src/aicoding/cli/parser.py`
- `src/aicoding/cli/handlers.py`
- `tests/unit/test_workflow_start.py`
- `tests/integration/test_workflow_start_flow.py`

Missing contracts that should be authored first:

- request/response contract for profile-aware `workflow start`
- request/response contract for profile-aware `node create`
- persistence/selection rule for where the selected profile is stored before and after compile
- explicit legality contract for top-level profile starts through each profile's `applies_to_kind`

Current future-direction decisions already settled for this slice:

- all built-in `epic`, `phase`, `plan`, and `task` kinds should ship parentless-capable
- top-level profile starts should be legal through each profile's own `applies_to_kind`
- selected workflow profile should be stored on node versions and also frozen into compiled workflow context
- initial profile-aware startup should take `workflow_profile` but not first-class `layout_id`
- first migration posture should stay additive and version-oriented rather than introducing a large new profile-state table

Implementation subtasks that should appear in a real plan checklist:

- add `workflow_profile` and any approved `layout_id` field to the startup/create request models
- extend CLI parser flags for `workflow start` and `node create`
- extend CLI handlers to pass those fields to daemon routes
- validate profile applicability against the selected kind during startup and parentless creation
- preserve the stronger future rule that all shipped parentless built-in kinds and their profiles can start top-level without an epic wrapper
- update top-level title derivation and startup summaries only if profile context requires it

Tests and proof needed:

- unit tests for startup validation and top-level legality
- integration tests for CLI/API request round trips
- real E2E proof for top-level profile starts, including non-epic starts if those kinds ship parentless

Main dependencies:

- Slice A
- `plan/reconcilliation/01_top_level_node_hierarchy_reconciliation.md`

Main risk:

- mixing profile-aware startup with the still-unreconciled top-level hierarchy behavior could hardcode an epic-only path again

### Slice C: Profile-Aware Layout Resolution And Child Materialization

Primary goal:

- replace fixed kind-driven layout selection with profile-aware layout resolution and compatibility checks

Current real code surfaces:

- `src/aicoding/daemon/materialization.py`
- `src/aicoding/daemon/hierarchy.py`
- `src/aicoding/resources/yaml/builtin/system-yaml/layouts/`
- `tests/unit/test_materialization.py`
- `tests/e2e/test_flow_03_materialize_and_schedule_children_real.py`

Missing contracts that should be authored first:

- authoritative layout-selection contract: selected profile vs explicit layout override vs generated layout registration
- authoritative compatibility rules between node kind, selected profile, and chosen layout
- authoritative contract for child-role, child-profile, and expected-output metadata

Current future-direction decisions already settled for this slice:

- explicit `layout_id` should begin at materialization rather than startup/create
- generated layout registration must be reconciled against profile-aware default layout resolution rather than replaced silently
- registered generated layouts should outrank profile defaults once registered
- early profile-aware implementation should not add a first-class `effective_layout_id` column yet
- rigid step-order enforcement and concrete blocked mutation responses are part of the intended runtime contract, not optional UX polish

Implementation subtasks that should appear in a real plan checklist:

- add helper logic to resolve the effective profile-aware default layout
- validate layout compatibility against selected profile
- extend materialization responses with selected profile and selected layout metadata
- propagate child role/profile hints from the selected layout into materialization outputs where the runtime wants them inspectable
- define and prove blocked mutation behavior for attempts to merge or complete before required child materialization
- decide whether generated workspace layout registration remains kind-shaped only or also becomes profile-aware
- update dependency and scheduling assertions if child-role semantics become visible in the runtime payload

Tests and proof needed:

- unit tests for layout resolution and compatibility decisions
- integration tests for materialization through daemon and CLI
- real E2E proof that profile selection changes child layout behavior through the normal materialization path

Main dependencies:

- Slice A
- Slice B

Main risk:

- layout precedence can become ambiguous if generated layouts, explicit overrides, and profile defaults are all added without one frozen contract

### Slice D: Compiled Workflow Profile Context And Brief Generation

Primary goal:

- make workflow compilation freeze the selected profile, profile-derived obligations, and generated brief context into inspectable runtime state

Current real code surfaces:

- `src/aicoding/daemon/workflows.py`
- `src/aicoding/db/models.py`
- compiled workflow inspection routes already served from `src/aicoding/daemon/app.py`
- `tests/unit/test_workflows.py`

Missing contracts that should be authored first:

- authoritative compile-context contract for selected profile state
- authoritative brief-generation contract
- authoritative contract for required role coverage, required repository updates, and required verification obligations in compiled state
- persistence contract for where brief payload and profile-derived obligations live

Current future-direction decisions already settled for this slice:

- compile should freeze more profile-derived context rather than less
- selected profile id belongs on node versions
- richer effective profile, layout, ancestry, obligation, and brief payload belongs in compiled workflow context
- compile-context shape should be sectioned into stable areas such as `profile`, `layout`, `ancestry`, `obligations`, `brief`, `prompt_stack`, and `compile_variant`

Implementation subtasks that should appear in a real plan checklist:

- add profile resolution helpers to the compile path
- validate selected profile applicability and layout compatibility during compile
- validate child-role coverage where the selected layout/profile demands it
- freeze selected profile metadata into `compile_context`
- generate and persist the compiler-produced brief payload
- expose compile failure details for profile/layout incompatibility and missing role coverage clearly

Tests and proof needed:

- unit tests for compile-time profile validation
- unit/integration tests for brief content and compile-context persistence
- E2E proof that the selected profile visibly affects the compiled workflow state, not just the request payload

Main dependencies:

- Slice A
- Slice B
- Slice C

Main risk:

- freezing too little data into compile context will make inspection surfaces flaky or underpowered

### Slice E: Profile Inspection And Operator Surfaces

Primary goal:

- add the read surfaces needed to inspect kinds, profiles, compatible layouts, and generated briefs without reusing the wrong endpoint for everything

Current real code surfaces:

- `src/aicoding/daemon/app.py`
- `src/aicoding/daemon/models.py`
- `src/aicoding/cli/parser.py`
- `src/aicoding/cli/handlers.py`
- the existing `node kinds` route and CLI path

Missing contracts that should be authored first:

- authoritative `node types` response contract
- authoritative `node profiles` response contract
- authoritative `workflow brief` response contract
- authoritative repo-wide workflow-profile catalog route contract

Current future-direction decisions already settled for this slice:

- `node kinds` should stay thin
- `node types` should be the richer node-context surface
- `workflow brief` should be a compact but substantial decision/context payload rather than a full catalog dump
- new inspection routes should stay additive and non-overlapping rather than mutating old thin routes into multi-mode contracts

Implementation subtasks that should appear in a real plan checklist:

- add daemon routes for `node types`, `node profiles`, and `workflow brief`
- decide whether `node kinds --verbose` is needed or whether `node types` remains the richer node-context surface
- add CLI parser and handler entries for the new inspection commands
- add API and CLI response models for the new surfaces
- ensure the surfaces derive from one shared helper layer rather than duplicating profile-resolution logic across handlers

Tests and proof needed:

- integration tests for each daemon route
- CLI tests for parser and handler wiring
- real E2E proof that profile and layout inspection work against real runtime state rather than synthetic fixtures only

Main dependencies:

- Slice A
- Slice B
- Slice C
- Slice D

Main risk:

- implementing these reads before compile/materialization contracts are frozen will create response shapes that drift immediately

### Slice F: Prompt-Pack And Prompt-Selection Adoption

Primary goal:

- move the draft prompt bundle from future-plan assets into a real runtime-owned prompt-selection model after the workflow-profile contracts are stable

Current real code surfaces:

- `src/aicoding/resources/prompts/`
- prompt references currently embedded in built-in YAML
- draft prompt assets under `plan/future_plans/workflow_overhaul/prompts/`

Missing contracts that should be authored first:

- authoritative prompt-reference naming contract
- authoritative prompt-stack composition contract for profile-aware compilation
- authoritative policy for which prompt text is compile-frozen vs runtime-looked-up

Current future-direction decisions already settled for this slice:

- prompt-bundle promotion should be handled as one coherent authoritative planning slice
- prompt files should not be promoted piecemeal across unrelated runtime slices

Implementation subtasks that should appear in a real plan checklist:

- normalize prompt reference naming if the schema changes require it
- move selected prompt assets from `plan/future_plans/workflow_overhaul/prompts/` into real prompt-pack locations
- update built-in YAML and compile logic to use the real references
- ensure prompt-stack composition remains inspectable through the future brief and workflow inspection surfaces

Tests and proof needed:

- prompt rendering and reference-validation tests
- compile/integration tests that prove prompt references resolve correctly
- E2E proof only where prompt choice materially affects runtime-visible decomposition behavior

Main dependencies:

- Slice A
- Slice D

Main risk:

- promoting prompt files too early will make the runtime look more complete than the actual profile-aware enforcement layer really is

### Slice G: Verification, E2E Mapping, And Checklist Adoption

Primary goal:

- make the whole family real in the repository's proving system instead of stopping at code plus draft notes

Current real code surfaces:

- `tests/unit/`
- `tests/integration/`
- `tests/e2e/`
- `notes/catalogs/checklists/verification_command_catalog.md`
- existing feature/checklist/flow traceability surfaces

Missing contracts that should be authored first:

- authoritative feature-to-checklist mapping for the new slices
- authoritative E2E mapping for workflow-profile narratives
- canonical verification command definitions for each slice

Implementation subtasks that should appear in a real plan checklist:

- add or update feature plans, checklists, and command catalog entries
- map each slice to explicit bounded and real-runtime proof surfaces
- add the structural top-level policy proof for profile-aware startup
- add the narrative ladder suites already sketched in the future E2E matrix
- update relevant flow/checklist/traceability docs so completion status does not outrun proof

Tests and proof needed:

- the full bounded and real E2E suite set for the slices above
- document consistency tests for every authoritative family adopted or changed

Main dependencies:

- all earlier slices

Main risk:

- the repo could easily end up with partial profile support that looks impressive in code but is still untracked in checklists and under-proven in real runtime narratives

## Recommended Sequencing

The likely sequence should be:

1. Slice A
2. Slice B
3. Slice C
4. Slice D
5. Slice E
6. Slice F
7. Slice G

Reason:

- schema and validation need to exist before the runtime can use them safely
- startup/create need a selected profile before materialization and compilation can honor it
- materialization and compilation need stable contracts before inspection surfaces should be frozen
- prompt adoption should trail the contract and enforcement layer rather than leading it
- proving and checklist adoption should happen as each slice lands, but the main plan family should still treat Slice G as a distinct required workstream

## What Should Become Real Authoritative Plans Later

When this bundle is promoted, the future authoritative family should likely include:

- one umbrella sequencing or reconciliation plan for the family
- one feature plan per slice above, or per tightly related pair of slices where the code boundary is truly shared
- one task plan per actual implementation batch
- checklist updates tied to each feature plan rather than one giant workflow-overhaul checklist line

The current future bundle is enough to derive those plans, but it is not itself already in that format.

## Minimum Promotion Standard

This future bundle should not be considered ready for promotion into implementation until each future slice has:

- an authoritative contract note where the current bundle still has only a draft
- a repo-grounded implementation checklist tied to real code files
- explicit canonical verification commands
- an affected-systems accounting across database, CLI, daemon, YAML, prompts, website, notes, and tests where applicable
- checklist and E2E traceability targets

## Practical Conclusion

The current workflow-overhaul bundle is best treated as a design incubator plus asset draft set.

The next real planning step, when implementation is actually desired, should be:

1. open an umbrella authoritative sequencing plan
2. open Slice A and Slice B as the first real authoritative feature plans
3. freeze the missing contracts those slices depend on
4. only then start coding

That approach matches the current codebase shape much better than trying to promote the whole bundle in one move.
