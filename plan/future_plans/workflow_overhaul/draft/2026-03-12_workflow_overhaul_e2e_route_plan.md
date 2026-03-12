# Workflow Overhaul E2E Route Plan

## Purpose

Lay out the full future real-E2E route set for the workflow-overhaul direction.

This note is the route-planning companion to the existing profile E2E matrix.

It is not an implementation claim.

## Why This Note Exists

The workflow-overhaul bundle already had:

- draft workflow profiles
- draft prompts
- draft compiled subtask-chain simulations
- a profile-to-suite E2E coverage matrix

What was still missing was the concrete route plan:

- which end-to-end journeys actually need to exist
- what each route must prove
- which adversarial checks each route must include
- what future suite file should own each route

This note fills that gap.

## Route Planning Rules

Every route in this plan should:

- use the real CLI and daemon boundary
- prove workflow-profile-aware compile and runtime behavior through durable state
- include at least one blocked or adversarial assertion when the route involves rigid workflow enforcement
- avoid direct DB shortcuts that bypass the intended operator/runtime path
- remain honest about whether it is proving CLI, daemon, YAML, prompts, and website surfaces

## Planned Route Set

### Route 00: Parentless Profile Start

- Planned file: `tests/e2e/test_e2e_workflow_profile_parentless_start_real.py`
- Goal: prove that any shipped parentless-capable kind can start with a selected workflow profile.
- Main path:
  - start `epic`, `phase`, `plan`, and `task` top-level nodes through the real startup surface
  - inspect selected profile, compiled context, and run posture
- Main assertions:
  - top-level legality is structural, not epic-only
  - selected profile is durably visible on the created version and compiled workflow
  - startup remains inspectable without hidden state

### Route 01: Planning Ladder

- Planned file: `tests/e2e/test_e2e_workflow_profile_planning_ladder_real.py`
- Goal: prove the planning-oriented decomposition ladder from `epic.planning` down to planning-oriented task profiles.
- Main path:
  - start `epic.planning`
  - inspect `workflow brief`, `node types`, and `node profiles`
  - materialize phase, plan, and task descendants
- Main assertions:
  - required planning roles appear at each tier
  - the compiled workflow preserves the planning-oriented child-profile mapping
  - the route does not collapse into implementation-first child selection

### Route 02: Feature Delivery Ladder

- Planned file: `tests/e2e/test_e2e_workflow_profile_feature_delivery_real.py`
- Goal: prove feature-delivery decomposition from `epic.feature` through discovery, implementation, docs, and E2E descendants.
- Main path:
  - start `epic.feature`
  - materialize children through phase, plan, and task tiers
  - inspect descendant profile choices and obligations
- Main assertions:
  - `discovery`, `implementation`, `documentation`, and `e2e` bands all exist
  - documentation and E2E obligations remain structurally visible
  - parent tiers do not absorb descendant-owned implementation

### Route 03: Review And Remediation Ladder

- Planned file: `tests/e2e/test_e2e_workflow_profile_review_remediation_real.py`
- Goal: prove review, remediation, and re-review as separate descendants rather than one collapsed task stream.
- Main path:
  - start `epic.review`
  - materialize review-focused descendants
  - drive review, remediation, and re-review steps through runtime-visible surfaces
- Main assertions:
  - review and remediation roles remain structurally distinct
  - remediation stays traceable back to findings
  - re-review depends on remediation output rather than implied closure

### Route 04: Documentation Ladder

- Planned file: `tests/e2e/test_e2e_workflow_profile_documentation_ladder_real.py`
- Goal: prove documentation-specific decomposition from `epic.documentation` through authoring, verification, and remediation descendants.
- Main path:
  - start `epic.documentation`
  - materialize documentation descendants
  - inspect docs-specific verification and remediation posture
- Main assertions:
  - inventory, authoring, verification, and remediation bands exist
  - docs verification cannot be silently skipped
  - docs closure remains inspectable at parent and descendant levels

### Route 05: Blocked Completion Before Spawn

- Planned file: `tests/e2e/test_e2e_workflow_profile_children_required_before_completion_real.py`
- Goal: prove that non-leaf profiles cannot merge or complete before spawning required children.
- Main path:
  - start a decomposition-required non-leaf node
  - attempt merge or completion before child materialization
- Main assertions:
  - daemon returns concrete `4xx`
  - machine code is `children_required_before_completion` or equivalent
  - blocked reason is visible in CLI and API inspection

### Route 06: Blocked Step Skip

- Planned file: `tests/e2e/test_e2e_workflow_profile_step_order_enforcement_real.py`
- Goal: prove rigid step order for non-leaf compiled chains.
- Main path:
  - attempt `merge_children` before `wait_for_children`
  - attempt `wait_for_children` before materialization where illegal
  - attempt completion after partial progress
- Main assertions:
  - skipped-step mutations fail rather than warn
  - the blocked response names the missing prior step or predicate
  - inspect surfaces show the current required step

### Route 07: Leaf Completion Predicate Enforcement

- Planned file: `tests/e2e/test_e2e_workflow_profile_leaf_completion_predicates_real.py`
- Goal: prove that `task.*` profiles cannot complete without required outputs, summaries, and proof.
- Main path:
  - run `task.implementation`, `task.review`, `task.verification`, `task.docs`, `task.e2e`, and `task.remediation` examples
  - attempt completion before the declared proof or output exists
- Main assertions:
  - completion is blocked until declared predicates are durably satisfied
  - the blocked reason is specific to the task type
  - successful completion records the required evidence honestly

### Route 08: Parent Merge Narrowness

- Planned file: `tests/e2e/test_e2e_workflow_profile_parent_merge_narrowness_real.py`
- Goal: prove that parents may reconcile, do basic bug checks, and docs alignment, but may not absorb child-owned implementation work.
- Main path:
  - drive a non-leaf node to merge time
  - inspect or simulate merge-time parent actions
- Main assertions:
  - parent-owned merge/docs steps are bounded
  - new implementation is not accepted as parent-local merge work
  - documentation alignment remains legal when it is parent-owned

### Route 09: Blocked Recovery And Resume

- Planned file: `tests/e2e/test_e2e_workflow_profile_blocked_recovery_resume_real.py`
- Goal: prove that blocked-step state and current required step survive pause, restart, and resume.
- Main path:
  - pause a workflow in a blocked or waiting state
  - restart the daemon or recover the session
  - inspect and resume
- Main assertions:
  - blocked reason remains durable
  - current required step is preserved
  - resume does not silently bypass blocked legality

### Route 10: Regenerate And Recompile Under Profile Constraints

- Planned file: `tests/e2e/test_e2e_workflow_profile_regenerate_and_recompile_real.py`
- Goal: prove that regenerate, rectify, and recompile preserve selected-profile constraints and reevaluate derived obligations honestly.
- Main path:
  - create a profiled node
  - regenerate or rectify after changes
  - inspect updated compiled state
- Main assertions:
  - selected profile remains visible across versions where intended
  - recompile updates effective layout, child-role mapping, and blocked-step metadata honestly
  - stale compiled obligations are not silently reused

### Route 11: Operator Inspection Route

- Planned file: `tests/e2e/test_e2e_workflow_profile_operator_inspection_real.py`
- Goal: prove the read surfaces for profile-aware runtime state.
- Main path:
  - call `workflow brief`, `node types`, `node profiles`, workflow inspection, and blocker inspection surfaces
- Main assertions:
  - selected profile, effective layout, role expectations, next legal step, and blocked reasons are visible
  - operator reads agree with daemon-owned state
  - child-profile recommendations are inspectable without opening raw YAML

### Route 12: Website Inspection And Bounded Actions

- Planned file: `tests/e2e/test_e2e_workflow_profile_web_inspection_real.py`
- Goal: prove the website UI rendering of profile-aware workflow state and bounded action legality.
- Main path:
  - open profile-aware nodes in the web UI
  - inspect rendered blocked reasons, required steps, and legal actions
  - trigger bounded legal and illegal actions
- Main assertions:
  - web UI reflects daemon-owned legality
  - blocked actions show the same reasons as CLI/API
  - browser-visible state stays consistent after route-changing mutations

## Recommended Implementation Order

1. Route 00: parentless profile start
2. Route 05: blocked completion before spawn
3. Route 06: blocked step skip
4. Route 07: leaf completion predicates
5. Route 11: operator inspection
6. Route 01: planning ladder
7. Route 02: feature delivery ladder
8. Route 03: review and remediation ladder
9. Route 04: documentation ladder
10. Route 09: blocked recovery and resume
11. Route 10: regenerate and recompile
12. Route 08: parent merge narrowness
13. Route 12: website inspection and bounded actions

## Coverage Intent

This route set should collectively prove:

- startup legality
- compiled workflow-profile state
- profile-aware decomposition
- rigid non-leaf enforcement
- rigid leaf completion predicates
- bounded parent merge behavior
- recovery safety
- operator inspectability
- web UI parity with daemon legality

## Non-Goals

This note does not try to:

- define the exact pytest implementation details for every route
- replace the broader repository-wide E2E feature matrix
- claim that workflow-profile-aware runtime support already exists
