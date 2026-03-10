# Workflow Profile E2E Matrix

## Purpose

Define how the draft workflow-profile bundle should eventually be proven through real runtime end-to-end narratives.

This note is a planning artifact.

It does not claim that profile-aware runtime support already exists.

## Goal

Map every current draft workflow profile to at least one future real-runtime E2E narrative that proves profile selection, inspection, decomposition, and downstream execution behavior through the actual workflow stack.

## Rationale

The workflow-overhaul bundle now contains:

- complete draft prompts across `epic`, `phase`, `plan`, and `task`
- starter workflow-profile YAMLs for all current draft profile ids
- rich layout examples extending through `plan -> task`

That design bundle now needs an equally explicit proving plan so the future implementation does not stop at:

- schema validation
- prompt-file existence
- unit coverage of profile lookup

The proving bar for this repository is real runtime evidence through real CLI, daemon, compiler, materialization, session, and inspection paths.

- Rationale: Profile-aware workflow support will be easy to under-prove if the repository stops at schema validation, prompt existence, or narrow profile-list inspection tests.
- Reason for existence: This plan exists to keep every draft epic, phase, plan, and task profile tied to future real-runtime proof before the workflow-profile bundle is promoted from design notes into implemented behavior.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`
- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/08_F05_default_yaml_library.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/43_F05_prompt_pack_authoring.md`
- `plan/features/65_F04_layout_replacement_and_hybrid_reconciliation.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`

## Required Notes

- `AGENTS.md`
- `plan/e2e_tests/00_e2e_feature_generation_strategy.md`
- `plan/e2e_tests/02_e2e_core_orchestration_and_cli_surface.md`
- `plan/e2e_tests/03_e2e_session_recovery_and_child_runtime.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/workflow_overhaul/starter_workflow_profiles/README.md`
- `plan/future_plans/workflow_overhaul/rich_layout_examples/README.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

## Scope

- Database: future profile-aware suites should assert durable selected-profile state, compiled brief content, and profile-derived materialization outputs through real runtime-visible reads.
- CLI: prove `workflow start`, `node create`, `node materialize-children`, `workflow brief`, `node types`, `node profiles`, and future profile-list/show surfaces through the real operator path.
- Daemon: prove profile applicability, layout compatibility, role coverage, brief generation, and inspection responses through the real daemon/compiler/materialization path.
- YAML: prove starter profile definitions and rich layout examples through runtime behavior rather than schema-only acceptance.
- Prompts: inspect the prompt-stack and brief/result surfaces that selected profiles expose in runtime-visible state.
- Notes: keep the profile-to-suite mapping explicit so future coverage work can be audited without claiming implementation is already complete.
- Tests: bias toward a small number of high-value real-runtime narratives rather than one shallow micro-test per profile.
- Performance: group profiles into narrative ladders where possible so the matrix remains real and maintainable.

## Realness Rules

Any future profile-aware E2E suite defined from this plan should:

- start or create workflows through the real operator surface once workflow-profile selection is implemented
- exercise compile/materialize/runtime paths through the actual daemon and CLI
- inspect `workflow brief`, `node types`, and `node profiles` through the real inspection surfaces
- prove that selected profiles affect layout choice, child role/profile mapping, and completion restrictions in durable runtime-visible ways
- avoid direct database setup or post-hoc state mutation shortcuts that bypass the intended runtime path

## Test Strategy

The profile matrix should not become one shallow test per profile.

Instead, future E2E coverage should be organized into a small set of narrative suites, each of which proves:

- top-level profile selection
- resulting child layout and recommended child profiles
- generated brief content
- downstream plan/task decomposition behavior
- runtime-visible inspection surfaces

Each suite should usually cover one dominant epic profile and the lower-tier profiles it naturally exercises.

Additional focused suites should exist only when a profile has behavior that would otherwise remain unproven.

## Proposed Future Suite Families

### Suite 1: Planning Profile Ladder

Proposed future file:

- `tests/e2e/test_e2e_workflow_profile_planning_ladder_real.py`

Purpose:

- prove that a planning epic selects the planning-oriented phase, plan, and task structures
- verify that planning-oriented decomposition produces requirements, architecture, planning, and verification-mapping roles rather than implementation-first roles

Main surfaces to exercise:

- `workflow start --workflow-profile epic.planning`
- `workflow brief --node <epic>`
- `node types --node <epic>`
- `node profiles --node <epic>`
- child materialization from epic to phase to plan to task

Primary profiles covered:

- `epic.planning`
- `phase.discovery`
- `phase.documentation`
- `plan.authoring`
- `plan.verification`
- `task.docs`
- `task.review`
- `task.verification`

Minimum assertions:

- selected workflow profile is frozen into runtime-visible state
- planning brief references the planning prompt stack and recommended child profiles
- materialized phase roles include `requirements`, `architecture`, `planning`, and `verification_mapping`
- downstream plans and tasks follow the recommended planning-oriented profiles rather than default feature-delivery behavior

### Suite 2: Feature Delivery Ladder

Proposed future file:

- `tests/e2e/test_e2e_workflow_profile_feature_delivery_real.py`

Purpose:

- prove the default feature-delivery shape from epic through task execution
- confirm that documentation and real-E2E obligations remain structurally visible and are not optional prompt fluff

Main surfaces to exercise:

- `workflow start --workflow-profile epic.feature`
- `workflow brief`, `node types`, and `node profiles`
- profile-aware materialization
- live implementation, docs-alignment, and real-E2E child flows

Primary profiles covered:

- `epic.feature`
- `phase.discovery`
- `phase.implementation`
- `phase.documentation`
- `phase.e2e`
- `plan.execution`
- `plan.authoring`
- `plan.verification`
- `task.implementation`
- `task.docs`
- `task.verification`
- `task.e2e`

Minimum assertions:

- feature epic materializes required `discovery`, `implementation`, `documentation`, and `e2e` roles
- phase and plan briefs reflect the selected lower-tier profile prompts
- the docs phase cannot disappear without violating role coverage
- the E2E phase carries real-proof obligations into plan/task layers

### Suite 3: Review And Remediation Ladder

Proposed future file:

- `tests/e2e/test_e2e_workflow_profile_review_remediation_real.py`

Purpose:

- prove that review-oriented work separates inspection, remediation, and re-review instead of collapsing them into one generic flow

Main surfaces to exercise:

- `workflow start --workflow-profile epic.review`
- `workflow brief`, `node types`, and `node profiles`
- review-focused child materialization
- evidence capture, remediation, and re-review runtime behavior

Primary profiles covered:

- `epic.review`
- `phase.review`
- `phase.remediation`
- `plan.authoring`
- `plan.execution`
- `plan.verification`
- `task.review`
- `task.remediation`
- `task.verification`

Minimum assertions:

- the selected review profile yields `scope_freeze`, `review`, `remediation`, and `re_review` phase roles
- review and remediation remain separate in runtime-visible child structures
- remediation tasks preserve traceability back to findings or failed proof surfaces
- re-review consumes remediation output rather than silently assuming closure

### Suite 4: Documentation Ladder

Proposed future file:

- `tests/e2e/test_e2e_workflow_profile_documentation_real.py`

Purpose:

- prove that documentation-oriented work chooses inventory, authoring, verification, and remediation bands rather than implementation-first decomposition

Main surfaces to exercise:

- `workflow start --workflow-profile epic.documentation`
- profile-aware brief and type/profile inspection surfaces
- documentation-centric child materialization
- document-schema-oriented downstream proof

Primary profiles covered:

- `epic.documentation`
- `phase.discovery`
- `phase.documentation`
- `phase.remediation`
- `plan.authoring`
- `plan.verification`
- `task.docs`
- `task.review`
- `task.remediation`

Minimum assertions:

- the documentation profile yields inventory/authoring/verification/remediation structure
- required repository updates and document-schema proving stay visible in brief and profile surfaces
- remediation remains available when authoring or verification reveals contradictions

### Suite 5: Profile Inspection And Override Surface

Proposed future file:

- `tests/e2e/test_e2e_workflow_profile_inspection_and_override_real.py`

Purpose:

- prove the operator-facing inspection and override surfaces that are profile-specific but do not require a full domain narrative each time

Main surfaces to exercise:

- `workflow profiles list`
- `workflow profiles show --profile <id>`
- `node types --node <id>`
- `node profiles --node <id>`
- `workflow brief --node <id>`
- explicit `--workflow-profile` and `--layout` override paths where legal

Primary profiles covered:

- all draft profile ids through list/show/inspection surfaces

Minimum assertions:

- every supported profile is visible with name, description, prompt ref, and default layout where applicable
- recommended child profiles are presented separately from the full legal option set
- explicit profile and layout overrides fail cleanly when incompatible

## Profile Coverage Table

### Epic profiles

- `epic.planning`: primarily proved by Suite 1
- `epic.feature`: primarily proved by Suite 2
- `epic.review`: primarily proved by Suite 3
- `epic.documentation`: primarily proved by Suite 4

### Phase profiles

- `phase.discovery`: primarily proved by Suites 1 and 2, with support in Suite 4
- `phase.implementation`: primarily proved by Suite 2
- `phase.documentation`: primarily proved by Suites 1, 2, and 4
- `phase.review`: primarily proved by Suite 3
- `phase.remediation`: primarily proved by Suites 3 and 4
- `phase.e2e`: primarily proved by Suite 2

### Plan profiles

- `plan.authoring`: primarily proved by Suites 1, 3, and 4
- `plan.execution`: primarily proved by Suites 2 and 3
- `plan.verification`: primarily proved by all four ladder suites

### Task profiles

- `task.implementation`: primarily proved by Suite 2
- `task.review`: primarily proved by Suites 1, 3, and 4
- `task.verification`: primarily proved by all four ladder suites
- `task.docs`: primarily proved by Suites 1, 2, and 4
- `task.e2e`: primarily proved by Suite 2
- `task.remediation`: primarily proved by Suites 3 and 4

## Required Runtime Behaviors To Prove

Every future suite should prove some subset of the following runtime behaviors, and the full family should prove all of them:

- profile selection is accepted only for compatible node kinds
- selected profile is frozen into compiled runtime-visible state
- default child layout comes from the selected profile rather than only the node kind
- recommended child profile mappings are visible in `workflow brief`
- supported profile and layout catalogs are visible in `node types` and `node profiles`
- profile-aware completion restrictions are inspectable and enforced
- lower-tier briefs are generated where the selected profile requires them
- materialized children inherit the intended role and recommended lower-tier profile shape
- incompatible profile/layout combinations fail with explicit operator-visible errors

## Suggested Bring-Up Order

1. Build Suite 5 first enough to prove inspection surfaces and profile selection/validation.
2. Build Suite 2 next because feature delivery exercises the widest cross-section of the profile ladder.
3. Build Suite 1 to prove planning-oriented divergence from feature defaults.
4. Build Suite 3 to prove review/remediation separation and traceable closure.
5. Build Suite 4 to prove documentation-specific decomposition and document-schema-heavy closure.

## Command And Evidence Expectations

When these suites are implemented, canonical commands should likely include:

- one focused invocation per new workflow-profile suite
- one aggregate invocation for all profile-aware E2E suites
- optional `-k` selections for individual dominant profiles when triaging failures

Each suite should leave evidence for:

- selected profile id
- selected layout id
- brief contents
- child role catalog
- recommended child-profile mappings
- real command outputs from execution and verification steps

## Relationship To Existing E2E Plans

This plan complements, rather than replaces:

- `plan/e2e_tests/00_e2e_feature_generation_strategy.md`
- `plan/e2e_tests/02_e2e_core_orchestration_and_cli_surface.md`
- `plan/e2e_tests/03_e2e_session_recovery_and_child_runtime.md`
- `plan/e2e_tests/04_e2e_quality_docs_provenance_audit.md`
- `plan/e2e_tests/05_e2e_git_rectification_and_cutover.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`

It exists specifically to add the missing profile-aware proving layer on top of that broader E2E doctrine.
