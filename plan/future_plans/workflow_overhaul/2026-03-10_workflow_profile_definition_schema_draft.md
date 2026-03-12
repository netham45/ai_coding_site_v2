# Workflow Profile Definition Schema Draft

## Purpose

Define a draft schema for the proposed `workflow_profile_definition` YAML family and show the minimum fields needed for the workflow-overhaul model to become structurally real.

This is a working draft for the workflow-overhaul bundle.

It is not an adopted repository schema.

## Design Goals

The schema should let the system declare:

- which stable node kind a profile applies to
- which layout the profile prefers
- which child roles are required
- which lower-tier profiles are implied
- which compiled subtask chain the future compiler is expected to emit
- which updates and verification categories are mandatory
- which completion claims are restricted
- whether a compiler-generated brief or work packet is required

The schema should not move legality or completion enforcement into YAML-only behavior.

## Draft Top-Level Shape

```yaml
kind: workflow_profile_definition
id: epic.feature
name: Feature Epic
description: Default epic profile for delivering a feature through implementation and proof.
applies_to_kind: epic
profile_family: epic
status: draft
main_prompt_ref: prompts/epic/feature.md
default_child_layout: layouts/epic_feature_to_phases.yaml
compatible_layouts:
  - layouts/epic_feature_to_phases.yaml
layout_tags:
  - feature_delivery
  - requires_docs_band
  - requires_real_e2e_band
child_generation:
  allowed_child_kinds: [phase]
  required_child_roles:
    - discovery
    - implementation
    - documentation
    - e2e
  allow_extra_roles: true
  min_children: 4
  max_children: 8
  balance_strategy: estimated_points
  max_point_skew_percent: 35
child_profile_defaults:
  discovery: phase.discovery
  implementation: phase.implementation
  documentation: phase.documentation
  e2e: phase.e2e
compiled_subtask_template:
  chain_family: non_leaf_decomposition
  child_target_kind: phase
  ordered_steps:
    - load_workflow_brief
    - review_required_child_roles
    - compose_phase_layout
    - validate_role_coverage
    - materialize_phase_children
    - confirm_child_spawn_summary
    - wait_for_children
    - merge_children
    - publish_parent_summary
  blocked_transitions:
    - action: merge_children
      code: children_not_ready_for_merge
      message: child closure predicates are not yet satisfied for merge
    - action: complete
      code: children_required_before_completion
      message: you did not spawn children before attempting merge or completion
  completion_predicates:
    - required child-role coverage exists
    - required child nodes were materialized
    - child closure state allows merge
    - parent summary was durably written
required_repository_updates:
  - notes
  - checklist
  - development_log
required_verification:
  - bounded_tests
  - real_e2e
completion_restrictions:
  forbidden_statuses_until_requirements_met:
    - complete
    - flow_complete
    - release_ready
brief_generation:
  require_compiler_generated_brief: true
  brief_prompt_ref: prompts/epic/global_brief.md
  include_node_tier_prompt: true
  include_profile_prompt: true
  include_recommended_child_profiles: true
  include_cli_discovery_note: true
metadata:
  intent: feature_delivery
  maturity: starter_builtin
```

## Proposed Field Set

### Required fields

- `kind`
- `id`
- `name`
- `description`
- `applies_to_kind`
- `profile_family`
- `main_prompt_ref`
- `child_generation`

### Strongly recommended fields

- `default_child_layout`
- `compatible_layouts`
- `layout_tags`
- `child_profile_defaults`
- `compiled_subtask_template`
- `required_repository_updates`
- `required_verification`
- `completion_restrictions`
- `brief_generation`

### Optional fields

- `status`
- `metadata`

## Proposed Nested Sections

### `child_generation`

Purpose:

- define the structural expectations for generated children

Suggested fields:

- `allowed_child_kinds`
- `required_child_roles`
- `allow_extra_roles`
- `min_children`
- `max_children`
- `balance_strategy`
- `max_point_skew_percent`

### `child_profile_defaults`

Purpose:

- map child role names to lower-tier workflow profiles

Example:

```yaml
child_profile_defaults:
  discovery: phase.discovery
  implementation: phase.implementation
  documentation: phase.documentation
  e2e: phase.e2e
```

### `completion_restrictions`

Purpose:

- declare which stronger status labels remain illegal until profile obligations are met

Suggested fields:

- `forbidden_statuses_until_requirements_met`

Runtime interpretation:

- this section declares obligation inputs for the compiler and daemon
- it does not make YAML the sole enforcement layer
- for non-leaf profiles with required child generation, the daemon should treat missing child materialization or missing required child-role coverage as a hard legality failure for the forbidden statuses

### `compiled_subtask_template`

Purpose:

- define the exact ordered compiled subtask chain the future compiler should emit for the profile
- expose blocked transitions and completion predicates in the same draft YAML surface as child-generation policy
- eliminate drift between profile YAML and the compiled-chain simulations

Suggested fields:

- `chain_family`
- `child_target_kind`
- `ordered_steps`
- `blocked_transitions`
- `completion_predicates`

Runtime interpretation:

- this section is still declarative input, not the sole runtime authority
- the compiler should turn `ordered_steps` into immutable compiled subtask records
- the daemon should reject skipped-step mutations and illegal completion attempts using the declared blocked-transition contract
- the CLI and website should surface the same ordered step list and blocked reasons for inspection

Recommended starter interpretation:

- `epic`, `phase`, and `plan` profiles use a `non_leaf_decomposition` chain family
- `task` profiles use a `leaf_execution` chain family
- non-leaf templates should always encode child materialization before `wait_for_children`, `merge_children`, or any completion-capable action
- leaf templates should always encode a final `validate_completion_predicates` stage before `complete_or_block`

### `brief_generation`

Purpose:

- declare whether the compiler must emit an epic or phase brief derived from this profile

Suggested fields:

- `require_compiler_generated_brief`
- `brief_prompt_ref`
- `include_node_tier_prompt`
- `include_profile_prompt`
- `include_recommended_child_profiles`
- `include_cli_discovery_note`

This section is mainly relevant for decomposing tiers such as `epic`, `phase`, and `plan`.

## Recommended Prompt Stack

The future brief or decomposition context should be assembled from multiple sources rather than one prompt only.

Recommended stack:

1. node-tier prompt
2. selected workflow-profile prompt
3. selected layout summary
4. recommended child role-to-profile mapping
5. CLI discovery note for the broader available child-profile set

Reason:

- the stable node kind still carries tier-wide responsibilities
- the selected profile carries the behavioral contract
- the layout carries the recommended child-role structure
- operators and AI contributors still need a discoverable path to the full available profile set rather than only the recommendation

## Recommended Child-Profile Guidance

The brief or decomposition context should include, for each recommended child:

- role
- recommended workflow profile id
- recommended workflow profile name
- recommended workflow profile description

Example:

```yaml
recommended_children:
  - role: documentation
    workflow_profile:
      id: phase.documentation
      name: Documentation Phase
      description: Align notes, commands, checklists, and process docs with implemented behavior.
```

## Recommended CLI Discovery Note

The brief or decomposition context should also tell the caller how to inspect the full available option set.

Recommended guidance:

- use `node types --node <id>` to inspect kinds, supported workflow profiles, compatible layouts, and role mappings
- use `node profiles --node <id>` when only the profile-focused view is needed

This keeps the generator or compiler from overclaiming that the recommended child profiles are the only legal choices.

## Vocabulary Recommendations

### `profile_family`

Keep this aligned with the stable node kind for the first implementation:

- `epic`
- `phase`
- `plan`
- `task`

### Starter verification vocabulary

Suggested reusable values:

- `bounded_tests`
- `integration_tests`
- `real_e2e`
- `document_schema`
- `performance_check`
- `resilience_check`

### Starter repository-update vocabulary

Suggested reusable values:

- `notes`
- `plan`
- `checklist`
- `development_log`
- `verification_commands`
- `e2e_mapping`

## Proposed Validation Rules

### Rule 1

`applies_to_kind` must match the major prefix in `id`.

Examples:

- `epic.feature` -> `applies_to_kind: epic`
- `phase.discovery` -> `applies_to_kind: phase`

### Rule 2

Every role mentioned in `child_profile_defaults` must also appear in `required_child_roles` unless a future extension explicitly allows optional-role defaults.

### Rule 3

`default_child_layout` must also appear in `compatible_layouts` when `compatible_layouts` is declared.

### Rule 4

`main_prompt_ref` and `brief_prompt_ref` must resolve against the prompt catalog when the family is adopted.

### Rule 5

Any `child_profile_defaults` value must point to a profile whose `applies_to_kind` is allowed by `allowed_child_kinds`.

### Rule 6

`forbidden_statuses_until_requirements_met` must use the repository's approved completion vocabulary only.

## Relationship To Other Families

### Node definitions

Node definitions should eventually point to:

- `default_workflow_profile`
- `supported_workflow_profiles`

### Layout definitions

Layouts should eventually point back to:

- compatible profile ids
- role-bearing child declarations

### Prompt assets

Profiles should choose prompt references, but prompts should not be the only place profile behavior exists.

### Compiler

The compiler should:

- resolve the selected profile
- validate profile/layout compatibility
- validate required child-role coverage
- freeze selected profile and derived obligations into compiled workflow context

## Recommended Enforcement Interpretation

The future workflow-overhaul model should interpret the profile schema through a code-owned enforcement ladder.

### Decomposition-required tiers

If a profile declares `child_generation.required_child_roles`, the future runtime should normally treat that profile as decomposition-required rather than leaf-executable.

That means the node is expected to:

- materialize children that cover the required roles
- delegate substantive implementation or proof work to those children
- use parent-local work only for narrow reconciliation operations

### Hard completion gate

For decomposition-required profiles, the daemon should reject any status listed in `completion_restrictions.forbidden_statuses_until_requirements_met` while any of the following are true:

- no children have been materialized
- required child roles are not covered
- required child outputs are not yet merged or otherwise accepted by the parent's closure rules
- required repository updates or verification categories are still unsatisfied

The intended operator-facing behavior is a concrete blocked mutation, not a soft hint.

Example future API posture:

- `4xx` response
- code such as `children_required_before_completion`
- message such as `you did not spawn children before attempting merge or completion`
- structured detail fields listing the unsatisfied conditions

### Step-order rigidity

The future runtime should treat compiled workflow steps and subtasks as rigidly ordered when the compiled workflow says they are ordered.

That means:

- step skipping is illegal
- merge or finalize steps should remain blocked until decomposition and required child progress steps are satisfied
- subtask completion should require the concrete durable records or command results declared by the compiled workflow contract

### Narrow reconciliation exception

Non-leaf tiers may still perform small parent-local operations when needed to reconcile child results, but the allowed scope should stay narrow:

- basic merge-conflict resolution
- basic integration bug checks exposed by combining child outputs
- documentation or checklist alignment that reflects the merged child results

Substantive new feature work discovered at a non-leaf tier should be pushed back into child remediation or explicit replan rather than silently completed at the parent.

## Suggested First Adoption Scope

If this family is implemented, the complete starter bundle in this note set now covers:

- `epic.planning`
- `epic.feature`
- `epic.review`
- `epic.documentation`
- `phase.discovery`
- `phase.implementation`
- `phase.documentation`
- `phase.review`
- `phase.remediation`
- `phase.e2e`
- `plan.authoring`
- `plan.execution`
- `plan.verification`
- `task.implementation`
- `task.review`
- `task.verification`
- `task.docs`
- `task.e2e`
- `task.remediation`

A first runtime adoption slice may still choose a smaller subset, but the design bundle is no longer limited to the top two tiers.
