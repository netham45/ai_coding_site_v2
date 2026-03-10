# Workflow Overhaul Working Notes

## Purpose

Preserve and elaborate the idea of making this repository's own development flow line up more closely with the orchestrator model it is building for other applications.

This is a working note, not an implementation plan.

The goal of this revision is to define the actual shape of the idea more concretely so it can be reviewed and iterated on before any implementation family is opened.

Associated planning-stage prompt drafts now live under:

- `plan/future_plans/workflow_overhaul/prompts/`

Practical companion notes for this bundle now also include:

- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_support_gap_closure.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_proposed_note_and_code_updates.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_definition_schema_draft.md`
- `plan/future_plans/workflow_overhaul/starter_workflow_profiles/`
- `plan/future_plans/workflow_overhaul/rich_layout_examples/`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_api_response_shapes.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_pydantic_model_draft.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_route_design.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_helper_assembly_draft.md`

## Current Observations

- The current built-in `epic`, `phase`, `plan`, and `task` ladder is structurally useful but semantically thin.
- Current built-in layout assets only describe child nodes, not the role each child plays inside a larger delivery pattern.
- Current built-in prompts are mostly tier-aware, not workflow-profile-aware.
- The current default layouts are too shallow to encode self-hosted repository work that explicitly separates planning, implementation, docs alignment, remediation, and real E2E proving.
- The repository's current decisions deliberately froze the active built-in ladder rather than silently changing runtime behavior.
- The original concept notes already expected stronger semantic differences across tiers than the current built-ins actually encode.

## Design Guardrails

- Keep the existing `epic -> phase -> plan -> task` ladder as the structural baseline.
- Do not introduce new node kinds such as `planning_epic`, `feature_epic`, `review_epic`, or `documentation_epic` as the first move.
- Treat those variations as declarative workflow profiles or epic styles layered onto the existing node kinds.
- Keep structure and policy declarative in YAML.
- Keep compilation, legality checks, balancing enforcement, completion gating, and state transitions code-owned.
- Do not let profile selection become a prompt-only behavior; runtime-visible policy must be declared and frozen into compiled state.

## Main Recommendation

The future direction should be profile-aware tiers, not kind proliferation.

That means:

- node `kind` remains `epic`, `phase`, `plan`, or `task`
- a separate declarative field selects the workflow profile
- that profile chooses:
  - which layout prompt to use
  - which default child layout to use
  - which child roles are required
  - which update obligations must be carried downward
  - which verification obligations must be satisfied before completion claims are allowed

This is a better fit for the current configurable hierarchy direction than adding many new kinds whose only purpose is prompt and policy selection.

## Why Profiles Instead Of New Kinds

Profiles are the cleaner future path because they:

- preserve the generic hierarchy substrate already established in current notes and code
- avoid making parent-child legality rules explode combinatorially
- let one tier keep a stable structural meaning while still allowing different operational contracts
- compose more naturally with project policy and prompt-pack selection
- give the daemon one clear place to validate required role coverage and closure obligations

New kinds may still become useful later, but they should be justified by structural differences, not merely by different decomposition prompts.

## Tier Contracts

The actual missing design asset is not only prompt wording.

The repository needs an explicit contract for what each tier is allowed and expected to decide.

### Epic

An epic should define delivery bands, not direct implementation tasks.

Epic responsibilities:

- translate a top-level request into a coherent set of `phase` children
- ensure the selected epic profile's required roles are covered
- choose only the minimum coherent phase set
- define sequencing, proof shape, and closure expectations at the product-effort level

Epic should not:

- directly define file-level implementation work
- create `task` children
- fragment work into speculative bands with no distinct contract

### Phase

A phase should define execution slices inside one delivery band.

Phase responsibilities:

- translate one delivery band into `plan` children
- keep every plan inside the phase's declared role and objective
- make per-plan outputs, dependencies, and proving intent explicit

Phase should not:

- re-plan the whole epic
- directly own unrelated work from other delivery bands
- handwave verification, note updates, or closure obligations

### Plan

A plan should define directly executable work packets.

Plan responsibilities:

- translate one plan goal into concrete `task` children
- specify artifact targets, verification commands, and required repository updates
- keep tasks concrete enough that they can execute without reinterpreting the plan

Plan should not:

- create vague "continue implementation" tasks
- split work with no execution, isolation, or dependency benefit
- hide docs, notes, checklist, log, or E2E linkage obligations in prose only

### Task

A task should execute one concrete work packet with closure obligations.

Task responsibilities:

- edit the necessary artifacts
- update required notes, logs, checklists, and plans where applicable
- run declared verification commands
- record durable success or failure summaries

Task should not:

- silently narrow scope
- claim completion without evidence
- invent new sibling work without escalating or failing clearly

## Proposed Workflow Profiles

The initial profile set worth exploring:

- `epic.planning`
- `epic.feature`
- `epic.review`
- `epic.documentation`

Supporting lower-tier profiles likely include:

- `phase.discovery`
- `phase.implementation`
- `phase.documentation`
- `phase.e2e`
- `phase.review`
- `phase.remediation`
- `plan.authoring`
- `plan.execution`
- `plan.verification`
- `task.implementation`
- `task.review`
- `task.verification`
- `task.docs`
- `task.e2e`
- `task.remediation`

These names are only draft vocabulary.

The important part is that each profile changes explicit contracts, not just prompt phrasing.

## What A Profile Must Control

A workflow profile should be able to declare:

- default child layout
- main decomposition prompt reference
- required child roles
- compatible layout ids or layout tags
- whether extra roles are allowed
- balancing targets or point-budget expectations
- required repository updates
- required verification categories
- completion-claim restrictions
- lower-tier default profile selection
- whether a compiler-generated epic brief is required for the tier

The generated decomposition context should likely include:

- the stable node-tier prompt for the current kind
- the selected workflow-profile prompt for the current profile
- the recommended child workflow profiles for the chosen layout roles
- short descriptions for those recommended child workflow profiles
- a note telling the operator or AI how to query the full available child-profile set from the CLI when it needs options beyond the recommended set

Examples:

- a `feature` epic should require implementation, docs alignment, and real E2E coverage
- a `review` epic should require review, remediation, and re-review loops
- a `documentation` epic should bias toward inventory, authoring, verification, and remediation rather than code implementation
- a `planning` epic should strongly favor requirements, architecture, and verification mapping over code changes

## Proposed New YAML Family

One useful future family is:

- `workflow_profiles/*.yaml`

Example draft:

```yaml
kind: workflow_profile_definition
id: epic.feature
name: Feature Epic
description: Default epic profile for delivering a feature through implementation and proof.
applies_to_kind: epic
default_child_layout: layouts/epic_feature_to_phases.yaml
main_prompt_ref: layout.generate_epic_feature
allowed_child_kinds: [phase]
required_child_roles:
  - discovery
  - implementation
  - docs
  - e2e
child_generation:
  min_children: 4
  max_children: 8
  enforce_required_roles: true
  allow_extra_roles: true
  balance_strategy: estimated_points
  max_point_skew_percent: 35
completion_requirements:
  required_updates:
    - notes
    - checklist
    - development_log
  required_verification:
    - bounded_tests
    - real_e2e
  forbid_overall_status:
    - complete
    - flow_complete
    - release_ready
  until_requirements_met: true
child_profile_defaults:
  discovery: phase.discovery
  implementation: phase.implementation
  docs: phase.documentation
  e2e: phase.e2e
```

This profile family would remain declarative.

The daemon/compiler would still decide:

- whether the selected profile exists and is valid
- whether required roles are satisfied
- whether the selected layout is compatible with the selected epic mode
- whether balancing constraints are acceptable
- whether completion claims are legal
- whether the generated epic brief matches the effective layout and profile inputs

## Proposed Node Definition Direction

The current node definition shape has one `main_prompt` per kind.

A future extension could look like this:

```yaml
node_definition:
  id: epic
  kind: epic
  tier: 0
  description: Top-level outcome-oriented planning container.
  main_prompt_ref: layout.generate_epic_generic
  default_workflow_profile: epic.feature
  supported_workflow_profiles:
    - epic.planning
    - epic.feature
    - epic.review
    - epic.documentation
  entry_task: research_context
  available_tasks:
    - research_context
    - execute_node
    - validate_node
    - review_node
  parent_constraints:
    allowed_kinds: []
    allowed_tiers: []
    allow_parentless: true
  child_constraints:
    allowed_kinds: [phase]
    allowed_tiers: [1]
    min_children: 0
    max_children: 12
  policies:
    max_node_regenerations: 3
    max_subtask_retries: 2
    child_failure_threshold_total: 3
    child_failure_threshold_consecutive: 2
    child_failure_threshold_per_child: 2
    require_review_before_finalize: false
    require_testing_before_finalize: false
    require_docs_before_finalize: false
    auto_run_children: true
    auto_rectify_upstream: false
    auto_merge_to_parent: false
    auto_merge_to_base: false
  hooks: []
```

The active implementation currently should not be changed to this shape silently.

This is a draft of the likely future direction only.

## Proposed Layout Definition Direction

The current layout definition only describes children structurally.

That is too weak for semantic profiles.

A future richer layout child likely needs fields such as:

- `role`
- `workflow_profile`
- `expected_outputs`
- `required_updates`
- `verification_targets`
- `estimated_points`

The selected layout should also be the source of truth for any generated epic-level briefing text.

The layout family may also need its own compatibility hints so layouts can say which epic modes they are intended to support.

Draft example:

```yaml
kind: layout_definition
id: epic_feature_to_phases
name: Feature Epic To Phases
description: Standard feature-delivery epic breakdown.
profile: epic.feature
compatible_workflow_profiles:
  - epic.feature
layout_tags:
  - implementation_heavy
  - requires_docs_band
  - requires_real_e2e_band
children:
  - id: discovery
    role: discovery
    workflow_profile: phase.discovery
    kind: phase
    tier: 1
    name: Discovery And Scope
    goal: Converge requirements, invariants, risks, and implementation boundaries.
    rationale: Implementation should not begin before the feature contract is explicit.
    expected_outputs:
      - notes updates
      - task plan
      - checklist update
    required_updates:
      - notes
      - plan
      - checklist
      - development_log
    verification_targets:
      - document_schema
    estimated_points: 3
    dependencies: []
    acceptance:
      - Required notes are updated for new constraints or ambiguities.
      - The implementation boundary is explicit enough to hand off to execution plans.
    ordinal: 1
  - id: implementation
    role: implementation
    workflow_profile: phase.implementation
    kind: phase
    tier: 1
    name: Implementation
    goal: Deliver the code and bounded proof.
    rationale: Runtime work should stay distinct from discovery and proving.
    expected_outputs:
      - code changes
      - bounded tests
    required_updates:
      - plan
      - checklist
      - development_log
    verification_targets:
      - bounded_tests
    estimated_points: 8
    dependencies: [discovery]
    acceptance:
      - The feature is implemented with bounded proof.
    ordinal: 2
  - id: docs
    role: docs
    workflow_profile: phase.documentation
    kind: phase
    tier: 1
    name: Documentation Alignment
    goal: Bring notes, commands, and checklists in line with implemented behavior.
    rationale: The repository forbids undocumented behavior drift.
    expected_outputs:
      - notes updates
      - checklist updates
      - command updates
    required_updates:
      - notes
      - checklist
      - development_log
    verification_targets:
      - document_schema
    estimated_points: 3
    dependencies: [implementation]
    acceptance:
      - Notes and checklists match actual behavior.
    ordinal: 3
  - id: e2e
    role: e2e
    workflow_profile: phase.e2e
    kind: phase
    tier: 1
    name: Real E2E Verification
    goal: Prove the feature through the intended runtime boundaries.
    rationale: Implemented is not complete without real E2E proof.
    expected_outputs:
      - E2E tests
      - verification results
    required_updates:
      - checklist
      - development_log
    verification_targets:
      - real_e2e
    estimated_points: 5
    dependencies: [implementation, docs]
    acceptance:
      - Canonical E2E commands pass for the intended scope.
    ordinal: 4
```

This should likely be bidirectional:

- epic modes declare the kinds of layouts they expect or allow
- layouts declare which epic modes they are valid for

The compiler should validate the intersection rather than trusting prompt text alone.

## Candidate Baseline Epic Styles

These are the first draft behavioral differences worth exploring.

### Planning Epic

Purpose:

- turn rough intent into explicit plans and verification mapping

Likely required phase roles:

- requirements
- architecture
- planning
- verification_mapping

Bias:

- avoid direct code implementation unless the user explicitly asks for a proof spike

### Feature Epic

Purpose:

- deliver a feature through discovery, implementation, docs alignment, and real proof

Likely required phase roles:

- discovery
- implementation
- docs
- e2e

Bias:

- balanced delivery across code, notes, checklist, and proving surfaces

### Review Epic

Purpose:

- inspect an existing system, identify issues, remediate them, and confirm the remediation

Likely required phase roles:

- scope_freeze
- review
- remediation
- re_review

Bias:

- evidence gathering, auditability, and remediation loops

### Documentation Epic

Purpose:

- inventory, author, verify, and repair authoritative docs

Likely required phase roles:

- inventory
- authoring
- verification
- remediation

Bias:

- note families, command alignment, schema rigidity, and repository status accuracy

## Compiler-Generated Epic Brief

The overhaul should plan for a separate global epic briefing surface.

This should not be a hand-authored second summary.

It should be generated by the compiler from:

- the selected epic workflow profile
- the effective `phase` layout definition
- the epic goal and acceptance criteria
- any required role-coverage, balance, or closure obligations attached to the profile

Purpose of the epic brief:

- combine the stable node-tier contract with the selected profile contract
- state the objective of the current node in a way that is inspectable and reusable
- name the recommended child role to child-profile mapping
- include enough operator-facing guidance that callers know when to accept the recommendation versus query the fuller available type/profile surface

- show the epic session the exact phase catalog it is expected to create or use
- explain why each phase exists
- expose dependencies, required outputs, and proof expectations
- prevent prompt-only reinterpretation of the phase ladder
- provide one inspectable frozen artifact for audit and CLI inspection later

The generated epic brief should include:

- epic profile name and intent
- overall epic goal
- required child-role coverage
- mode/layout compatibility notes describing why the selected layout is valid for the current epic mode
- one entry per selected phase containing:
  - phase id
  - phase role
  - phase title
  - phase goal
  - phase rationale
  - expected outputs
  - required updates
  - verification targets
  - dependencies
  - acceptance criteria
- any point-budget or balance requirements if the profile uses them
- any completion restrictions relevant at the epic tier

Important boundary:

- YAML declares the layout and profile data
- code/compiler generates the epic brief from that data
- prompt files should consume the generated brief, not manually recreate it

This keeps the phase catalog, prompt surface, and compiled audit artifact aligned.

## Blocking Summary Callback Stage

The overhaul should also plan for explicit human-facing summary checkpoints.

At key points in a workflow, the AI should be asked to provide a human-readable summary intended for user presentation.

This should not be treated as a best-effort side effect.

It should be modeled as an explicit workflow task or subtask that blocks progress until the AI calls back through the CLI with the required summary.

Purpose of this stage:

- give the user an intelligible update at important boundaries
- force the workflow to stop and emit a usable narrative before moving on
- avoid losing state in long-running trees where only internal artifacts exist
- create durable inspectable summary history tied to the exact stage that requested it

Likely key points include:

- after epic decomposition is agreed
- after a sub-epic or phase completes its planning pass
- before entering expensive implementation or E2E work
- after review findings are gathered
- before pausing for user input
- after remediation or finalize-ready states

This stage should differ from the current generic `write_summary` primitive in one important way:

- `write_summary` is a generic summary artifact operation
- the planned blocking summary callback stage is an explicit workflow gate that waits for a CLI-registered human-readable update before advancing

The intended runtime contract:

- the daemon reaches a summary-request stage
- the current session receives a prompt telling it to produce a user-facing summary
- the workflow remains blocked in that stage until a CLI callback such as `summary register` or a stricter dedicated summary-stage command is received
- once the callback succeeds, the workflow can advance

Draft future YAML shape:

```yaml
kind: task_definition
id: request_user_summary
name: Request User Summary
description: Block until the session registers a human-readable summary intended for the user.
applies_to_kinds:
  - epic
  - phase
  - plan
policy:
  max_subtask_retries: 2
  on_failure: pause_for_user
uses_reviews: []
uses_testing: []
uses_docs: []
subtasks:
  - kind: subtask_definition
    id: prompt_for_user_summary
    type: run_prompt
    title: Prompt For User Summary
    description: Ask the current session for a concise user-facing summary of the current state.
    prompt: "prompts/runtime/request_user_summary.md"
    outputs: []
    retry_policy: {max_attempts: 2, backoff_seconds: 5}
    on_failure: {action: pause_for_user}
  - kind: subtask_definition
    id: wait_for_user_summary_callback
    type: validate
    title: Wait For Summary Callback
    description: Block until the required summary has been registered through the CLI.
    requires: [{subtask_complete: prompt_for_user_summary}]
    command: "python3 -m aicoding.cli.main summary await --node {{node_id}} --type user_update"
    outputs: [{type: summary_written, path: summaries/user_update.md}]
    retry_policy: {max_attempts: 1, backoff_seconds: 0}
    on_failure: {action: pause_for_user}
```

The exact CLI shape can change.

The important contract is:

- the workflow explicitly asks for the summary
- the summary is durably registered
- the stage remains blocked until that registration occurs

This should also integrate with prompt and summary history so operators can inspect:

- which stage requested the user-facing summary
- when it was registered
- what text was shown to the user
- what node, version, run, and compiled stage it belonged to

## Prompt Strategy

The current prompt family should evolve by combining:

- one baseline prompt per tier
- short profile overlays or profile-specific variants

The baseline tier prompt should define:

- what the tier is for
- what the tier must not do
- what output contract it must satisfy
- what required updates and proof obligations must be carried forward

Profile overlays should then add:

- role-specific child-role expectations
- profile-specific prohibitions
- profile-specific success criteria

This should avoid proliferating entirely separate prompt packs unless the styles diverge heavily.

Planning-stage draft prompt files for the current four-tier workflow concept now exist under:

- `plan/future_plans/workflow_overhaul/prompts/epic/`
- `plan/future_plans/workflow_overhaul/prompts/sub_epic/`
- `plan/future_plans/workflow_overhaul/prompts/plan/`
- `plan/future_plans/workflow_overhaul/prompts/task/`

The epic prompt family should also expect a compiler-generated `epic_brief` input rather than relying only on raw request text and tier-local instructions.

## Proposed Prompt Reference Expansion

Future prompt references may need identifiers such as:

```yaml
kind: prompt_reference_definition
id: default_prompt_refs
name: Default Prompt References
description: Canonical prompt identifiers used by the built-in YAML library.
references:
  layout.generate_epic_generic: layouts/generate_epic_layout_generic.md
  layout.epic_global_brief: layouts/epic_global_brief.md
  layout.generate_epic_feature: layouts/generate_epic_layout_feature.md
  layout.generate_epic_planning: layouts/generate_epic_layout_planning.md
  layout.generate_epic_review: layouts/generate_epic_layout_review.md
  layout.generate_epic_documentation: layouts/generate_epic_layout_documentation.md
  layout.generate_phase_generic: layouts/generate_phase_layout_generic.md
  layout.phase_global_brief: layouts/phase_global_brief.md
  layout.generate_phase_discovery: layouts/generate_phase_layout_discovery.md
  layout.generate_phase_implementation: layouts/generate_phase_layout_implementation.md
  layout.generate_phase_documentation: layouts/generate_phase_layout_documentation.md
  layout.generate_phase_review: layouts/generate_phase_layout_review.md
  layout.generate_phase_remediation: layouts/generate_phase_layout_remediation.md
  layout.generate_phase_e2e: layouts/generate_phase_layout_e2e.md
  layout.generate_plan_generic: layouts/generate_plan_layout_generic.md
  layout.plan_global_brief: layouts/plan_global_brief.md
  layout.generate_plan_authoring: layouts/generate_plan_layout_authoring.md
  layout.generate_plan_execution: layouts/generate_plan_layout_execution.md
  layout.generate_plan_verification: layouts/generate_plan_layout_verification.md
  execution.execute_task_generic: execution/execute_task_generic.md
  execution.execute_task_implementation: execution/execute_task_implementation.md
  execution.execute_task_review: execution/execute_task_review.md
  execution.execute_task_verification: execution/execute_task_verification.md
  execution.execute_task_docs: execution/execute_task_docs.md
  execution.execute_task_e2e: execution/execute_task_e2e.md
  execution.execute_task_remediation: execution/execute_task_remediation.md
```

The exact identifiers can change.

The important part is separating:

- tier baseline intent
- profile-specific specialization

## Conflict Handling As Workflow Work

One likely future correction is to stop treating merge conflicts as only a git-level exception.

For this repository's intended model, many merge conflicts are actually one of three different things:

- a mechanical overlap that can be repaired inside the merged parent tree
- a semantic disagreement where sibling outputs are individually valid but incompatible together
- a planning or dependency defect where the child tasks, dependencies, or parent brief no longer describe a coherent merged outcome

That means future conflict handling should be staged rather than monolithic.

### Proposed Conflict Classes

#### Mechanical Conflict

Meaning:

- the merge failed at the file/content level
- the underlying task intent still appears compatible
- a bounded parent-local reconciliation pass may be able to produce one coherent merged result

Future allowed actions:

- inspect the conflicted files
- edit the merged parent tree
- rerun validations, review, and tests
- mark the conflict resolved only if the repaired merged result passes the required proof

#### Semantic Conflict

Meaning:

- the conflict is not only about markers or line overlap
- the sibling outputs disagree in API shape, behavior, invariants, or assumptions
- a plain textual merge is not sufficient evidence of correctness

Future allowed actions:

- run a profile-aware parent reconcile task
- compare the sibling outputs against the parent brief, acceptance criteria, and required child roles
- rewrite the merged result if that rewrite remains consistent with the existing plan and profile contract
- require stronger review or testing gates before resolution is accepted

#### Spec Or Dependency Conflict

Meaning:

- the conflict reveals stale or incomplete tasks, wrong sibling ordering, missing dependency declarations, or a parent brief that is no longer coherent
- the right answer is not only "fix the file"; it is "repair the workflow description that produced the incompatible outputs"

Future allowed actions:

- revise dependency edges
- revise or supersede child tasks or plans
- trigger a rectification or replan path
- rebuild from seed and replay current authoritative child finals after the workflow contract is repaired

This class should not be silently collapsed into a code edit.

### Proposed Resolution Stages

The likely future staged policy is:

1. detect the merge conflict and record it durably
2. classify whether it looks mechanical, semantic, or spec/dependency-driven
3. attempt bounded parent-local repair only for conflicts that remain inside the current plan/profile contract
4. rerun required proof for the repaired merge result
5. if repair fails or the conflict points to stale workflow structure, enter a rectification path instead of pretending the issue was only local code overlap
6. pause for user only when the runtime cannot make a defensible next move within the declared policy

This preserves the idea that "resolved" means more than "git markers are gone."

### Why This Belongs In Workflow Overhaul

The future workflow-overhaul direction already argues that tiers and profiles should carry explicit responsibilities, proof obligations, and update requirements.

Conflict handling belongs in that same family because the system should eventually decide:

- whether a parent `phase` or `plan` is allowed to auto-reconcile child outputs
- whether a profile requires re-review or re-test after semantic conflict repair
- whether documentation or note updates become mandatory after conflict-driven task or dependency revision
- whether a conflict is allowed to trigger replanning automatically or only with explicit operator approval

Put differently:

- mechanical repair is local merge work
- semantic repair is parent reconcile work
- spec/dependency repair is workflow rectification work

That distinction is workflow behavior, not only git behavior.

### Profile Implications

Future workflow profiles may need explicit conflict policy fields such as:

- whether auto-repair is allowed
- which conflict classes may be handled without human approval
- required proof after each conflict class
- whether dependency rewrites are permitted at the current tier
- whether a conflict should escalate to a higher-tier replan phase

Examples:

- a `feature` profile may allow bounded mechanical repair plus mandatory tests
- a `review` profile may require explicit findings and remediation records before accepting a semantic conflict repair
- a `documentation` profile may allow broader textual reconciliation while still forbidding silent structural drift
- a future high-safety profile may forbid any dependency or task rewrite without user approval

### Layout And Prompt Implications

If conflict handling becomes workflow-aware, layouts and prompts should stop assuming one generic "resolve merge conflict" action.

Future layouts may need to declare:

- which role owns conflict triage
- whether a separate remediation or rectification child is expected
- which artifacts must be updated when conflict-driven rework changes intent

Future prompts should distinguish:

- fix the merged code or document if the current plan still holds
- escalate when the conflict implies stale tasks, stale dependencies, or a broken parent brief

This keeps the model from hiding planning defects inside ad hoc merge edits.

### Compiler And Runtime Boundary

YAML should be able to declare future conflict policy and role obligations.

Code/runtime should remain authoritative for:

- conflict recording
- conflict classification heuristics or gating
- deciding whether a proposed action is legal at the current tier/profile
- rerunning verification and enforcing proof thresholds
- triggering rectification, supersession, or pause states

This remains consistent with the repository's code-versus-YAML delineation rule.

## Baseline Per-Tier Prompt Drafts

These are draft prompts for review, not active runtime assets.

### Epic Prompt Draft

```text
You are defining child `phase` nodes for epic `{{node_id}}`.

Role of this tier:
- turn one top-level effort into delivery bands
- ensure the selected epic profile's required roles are covered
- choose only the minimum coherent set of phases

Do not:
- define file-level implementation work
- create tasks directly
- split work into speculative phases with no distinct contract

Inputs:
- user request: `{{user_request}}`
- epic profile: `{{workflow_profile}}`
- epic goal: `{{node.title}}`
- acceptance criteria: `{{acceptance_criteria}}`
- required child roles: `{{required_child_roles}}`
- policy constraints: `{{policy_constraints}}`
- compiled epic brief: `{{epic_brief}}`

Your job:
- produce a `layout_definition` for `phase` children
- assign each child a `role`
- ensure required roles are covered exactly once unless duplication is justified
- keep dependencies minimal and real
- stay aligned with the compiler-generated epic brief unless the workflow explicitly enters a replan path

Each child must include:
- `id`
- `role`
- `workflow_profile`
- `name`
- `goal`
- `rationale`
- `expected_outputs`
- `required_updates`
- `dependencies`
- `acceptance`
- `ordinal`

Return JSON only:
{"status":"OK","child_count":<n>,"coverage":{"missing_roles":[],"extra_roles":[]}}
or
{"status":"FAIL","message":"<reason>"}
```

### Phase Prompt Draft

```text
You are defining child `plan` nodes for phase `{{node_id}}`.

Role of this tier:
- break one delivery band into executable plan slices
- make each plan independently understandable and reviewable
- preserve the phase boundary rather than re-planning the whole epic

Do not:
- create tasks directly unless the phase clearly collapses to one plan with one task downstream
- create plans that differ only cosmetically
- leave verification or required updates implicit

Inputs:
- phase profile: `{{workflow_profile}}`
- phase role: `{{node_role}}`
- phase goal: `{{node.title}}`
- acceptance criteria: `{{acceptance_criteria}}`
- relevant notes and context: `{{context_bundle}}`

Your job:
- produce the minimum coherent set of `plan` children
- each plan must own one clear execution boundary
- each plan must state artifact targets and proving intent

Each child must include:
- `name`
- `goal`
- `rationale`
- `expected_outputs`
- `required_updates`
- `verification_targets`
- `dependencies`
- `acceptance`

Return JSON only:
{"status":"OK","child_count":<n>}
or
{"status":"FAIL","message":"<reason>"}
```

### Plan Prompt Draft

```text
You are defining child `task` nodes for plan `{{node_id}}`.

Role of this tier:
- turn one plan into directly executable work packets
- make the tasks concrete enough that a worker can act without re-planning

Do not:
- create vague "continue implementation" tasks
- hide docs, notes, checklist, log, or test obligations in prose
- split work unless it improves execution, isolation, or dependency management

Inputs:
- plan profile: `{{workflow_profile}}`
- plan goal: `{{node.title}}`
- plan acceptance criteria: `{{acceptance_criteria}}`
- targeted files or surfaces: `{{artifact_targets}}`
- required updates: `{{required_updates}}`
- verification commands: `{{verification_targets}}`

For each task, specify:
- exact implementation goal
- likely files or surfaces touched
- required docs, notes, checklist, and log updates
- bounded verification commands
- E2E linkage if applicable
- explicit acceptance criteria

Return JSON only:
{"status":"OK","child_count":<n>}
or
{"status":"FAIL","message":"<reason>"}
```

### Task Prompt Draft

```text
You are executing task `{{node_id}}`.

Role of this tier:
- complete one concrete work packet
- update all required repository artifacts
- run the declared verification commands
- fail explicitly if blocked

Do not:
- silently narrow the task
- claim success without evidence
- invent new scope unless you record a blocker or replan trigger

Inputs:
- task profile: `{{workflow_profile}}`
- task goal: `{{node.title}}`
- acceptance criteria: `{{acceptance_criteria}}`
- artifact targets: `{{artifact_targets}}`
- required updates: `{{required_updates}}`
- verification commands: `{{verification_commands}}`
- governing plan: `{{governing_plan_path}}`

Required work:
- inspect current context and relevant notes first
- make the smallest coherent change that satisfies the task
- update required notes, checklists, and development logs if the task requires them
- run the declared commands
- register summaries and failures durably through the CLI

Completion rule:
- complete only if artifacts exist and commands actually passed
- otherwise fail with a concise blocker summary and next required step
```

## Profile-Specific Prompt Overlays

Short overlays are likely better than immediately creating entirely separate full prompts for every profile.

### Planning Epic Overlay

- optimize for requirements, architecture, plan authoring, and verification mapping
- avoid code-heavy phases unless explicitly requested
- require explicit note and command outputs

### Feature Epic Overlay

- require implementation plus documentation alignment plus real E2E proof
- bias against stopping at bounded proof only

### Review Epic Overlay

- require evidence gathering, remediation, and re-review
- prefer inspection and diagnosis surfaces over speculative redesign

### Documentation Epic Overlay

- require inventory, authoring, verification, and remediation
- bias toward authoritative docs, command alignment, and consistency tests

## Runtime And Compiler Expectations

If this idea is promoted into implementation work later, the daemon and compiler should be responsible for:

- validating selected workflow profiles
- freezing the effective profile into compiled workflow state
- validating required child roles
- enforcing completion restrictions
- carrying required updates and verification obligations into compiled tasks
- rejecting obviously invalid or wildly imbalanced decompositions when policy says to do so

YAML should not decide at runtime whether the current decomposition is acceptable.

That remains an authoritative runtime/compiler job.

## Likely First Implementation Sequence

1. Add an authoritative note that freezes tier contracts and workflow-profile vocabulary.
2. Add schema/model support for workflow profiles and richer layout children.
3. Add built-in profile YAML and profile-aware prompt references.
4. Extend layout-generation prompts to be profile-aware.
5. Freeze selected profile and closure obligations into compiled workflow state.
6. Add daemon validation for required child roles and completion requirements.
7. Add bounded tests, then at least one real E2E narrative per profile family or grouped proof narrative.

## Open Questions

- Should workflow profiles be a standalone YAML family or a sub-document under node definitions or policy definitions?
- Should profile selection live on the node itself, in project policy, or both with project policy providing defaults and node creation allowing overrides?
- Should `planning`, `feature`, `review`, and `documentation` be the user-visible vocabulary, or should the public names be more operationally explicit?
- Should documentation verification and remediation always be distinct roles, or should that remain profile-configurable?
- How much balancing metadata is worth carrying in v1 of the profile design before it becomes overfit?
- Which required updates belong on the child layout versus on the workflow profile default versus on the compiled task payload?
- How should the compiled workflow expose these obligations for CLI inspection?

## Promotion Rule

If work on this idea actually begins, this note should be translated into:

- one or more authoritative task plans under `plan/tasks/`
- one or more authoritative notes under `notes/planning/implementation/` or another implementation-facing family
- any required feature-plan or note updates
- YAML and prompt asset changes
- bounded and E2E proving targets

Until then, this note is a concrete future design draft rather than an implementation commitment.
