# Project Development Flow Doctrine

## Purpose

This document is the high-level development flow for this repository.

It is intended to keep planning, implementation, bounded verification, hardening, and real end-to-end verification aligned with:

- the original project vision
- the major feature inventory
- the per-feature implementation decision notes
- the audit and flow checklists
- the real E2E hardening track

This document is deliberately written as a process doctrine rather than a single implementation ticket.

---

## Artifact Coverage

This process doctrine is expected to be used together with the following existing repository artifacts.

### Core inventory and traceability

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`
- `notes/catalogs/traceability/simulation_flow_union_inventory.md`
- `notes/catalogs/traceability/action_automation_matrix.md`

### Audit and checklist artifacts

- `notes/catalogs/audit/auditability_checklist.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/audit/yaml_builtins_checklist.md`
- `notes/catalogs/checklists/feature_checklist_standard.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

### Scenario and flow planning artifacts

- `notes/scenarios/journeys/common_user_journeys_analysis.md`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`
- `notes/scenarios/walkthroughs/hypothetical_plan_workthrough.md`
- `notes/planning/implementation/scenario_and_flow_pytest_plan.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`
- `notes/planning/implementation/full_real_end_to_end_flow_hardening_plan.md`
- `notes/planning/implementation/missing_simulation_flow_yaml_and_test_plan.md`
- `notes/planning/implementation/real_e2e_flow_contract_phase1_decisions.md`

### Per-feature implementation decision artifacts

The current implementation-planning pass includes the feature and setup decision notes under:

- `notes/planning/implementation/*_decisions.md`

This currently includes the per-feature implementation decision notes for:

- daemon authority and durable orchestration record
- configurable node hierarchy
- YAML schema system
- durable node lifecycle state
- node versioning and supersession
- source document lineage
- immutable workflow compilation
- default YAML library
- project policy extensibility
- override and merge resolution
- dependency graph and admission control
- deterministic branch model
- node run orchestration
- AI-facing CLI command loop
- operator CLI and introspection
- session binding and resume
- provider-agnostic session recovery
- idle detection and nudge behavior
- optional pushed child sessions
- child node spawning
- manual tree construction
- conflict detection and resolution
- child merge and reconcile pipeline
- regeneration and upstream rectification
- validation framework
- review framework
- hook system
- testing framework integration
- user gating and pause flags
- failure escalation and parent decision logic
- prompt history and summary history
- code provenance and rationale mapping
- documentation generation
- automation of all user-visible actions
- auditable history and reproducibility
- optional isolated runtime environments
- top-level workflow creation commands
- stage context retrieval and startup context
- tmux session manager
- idle screen polling and classifier
- variable substitution and context rendering
- subtask library authoring
- prompt pack authoring
- validation/review/testing/docs/rectification schema families
- runtime policy and prompt schema families
- AI CLI bootstrap and work retrieval commands
- AI CLI progress and stage transition commands
- operator structure and state commands
- operator history and artifact commands
- session attach, resume, and control commands
- source discovery and loading pipeline
- schema validation compile stage
- override resolution compile stage
- hook expansion and policy resolution compile stage
- rendering and compiled payload freeze stage
- compiled workflow persistence and failure diagnostics
- database runtime state schema family
- database session attempt history schema family
- database provenance/docs/audit schema family
- built-in node/task/layout library authoring
- built-in validation/review/testing/docs library authoring
- built-in runtime policy/hook/prompt library authoring
- candidate and rebuild compile variants
- richer child scheduling and blocker explanation
- layout replacement and hybrid reconciliation
- execution orchestration and result capture
- provider-specific session recovery surface
- failure taxonomy and parent decision matrix
- turnkey quality gate finalize chain
- live rebuild cutover coordination
- live git merge and finalize execution
- expanded human intervention matrix
- multilanguage provenance expansion

### Pseudocode and state-model artifacts

- `notes/pseudocode/README.md`
- `notes/pseudocode/state_machines/*.md`
- `notes/pseudocode/modules/*.md`
- `notes/pseudocode/pseudotests/*.md`
- `notes/pseudocode/results/*.md`

---

## 1. Genesis

Start with a rough outline or brain dump.

Define:

- the rough product scope
- the main systems every feature may affect
- the likely implementation stack
- the high-level boundaries of responsibility

Typical systems:

- database
- backend / daemon / app
- CLI or API
- UI if applicable
- YAML / config / schema layers
- prompts
- documentation / notes
- testing / audit / observability

Goals of this stage:

- define what the product is supposed to do
- define the rough feature set
- define what technologies will be used
- ask for review of logic holes, unstated assumptions, and missing required behavior

Also identify early system invariants:

- what must never happen
- what data must always exist
- what state transitions are legal
- what recovery guarantees are required

Primary artifacts to consult or update during this stage:

- `notes/explorations/original_concept.md`
- `notes/explorations/musings.md`
- `notes/catalogs/inventory/major_feature_inventory.md`

---

## 2. Plan Creation

Turn the rough idea into a coherent design model.

Define:

- database tables and durable state
- sources of truth
- system boundaries
- API protocols
- concurrency expectations
- storage model
- recovery model
- audit model
- code vs config / YAML boundaries
- prompt roles
- command surfaces

Goals of this stage:

- standardize how the system works before coding
- prevent overlapping implementations of the same concept
- force architectural decisions to become explicit

At this stage, also define canonical verification commands:

- bootstrap command
- migration command
- unit test command
- integration test command
- E2E command
- performance command
- parallel-safe command posture for the same layers

Primary artifacts to consult or update during this stage:

- `notes/specs/architecture/authority_and_api_model.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`

---

## 3. Plan Development

Break the architecture into feature plans, setup plans, checklists, and cross-system requirements.

For each major feature, determine:

- database impact
- CLI / API impact
- daemon / backend impact
- YAML / schema impact
- prompt impact
- documentation / notes impact
- observability / audit impact
- testing impact
- performance impact
- recovery / concurrency impact

Goals of this stage:

- define how features interact
- identify conflicts, impossibilities, and missing dependencies
- make hidden cross-system work visible

Required supporting artifacts:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/checklists/feature_checklist_standard.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`
- `notes/planning/implementation/*_decisions.md`

Rule:

- every feature should explicitly list affected systems
- if a system is not affected, that should be a deliberate conclusion
- features should identify the invariants they depend on or introduce

---

## 4. Before Development

Generate expected user flows and operator flows before implementation starts.

Ask for:

- predicted user journeys
- operator journeys
- recovery journeys
- failure journeys
- concurrency/conflict scenarios
- abandoned/partial-completion paths
- impossible/blocking scenarios

Then simulate them from:

- user action
- CLI/API call
- daemon/application behavior
- database state change
- resulting inspectability/audit output

Use this stage to find:

- missing behavior
- hidden dependencies
- contradictions
- unhandled recovery cases
- bad source-of-truth assumptions

Primary artifacts:

- `notes/scenarios/journeys/common_user_journeys_analysis.md`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`
- `notes/scenarios/walkthroughs/hypothetical_plan_workthrough.md`
- `notes/planning/implementation/scenario_and_flow_pytest_plan.md`
- `notes/planning/implementation/missing_simulation_flow_yaml_and_test_plan.md`

### Pseudocode and state logic

Use pseudocode or state-modeling for:

- state transition tables
- failure handling logic
- dependency/readiness logic
- retry/recovery behavior
- parent/child orchestration
- cutover / finalize rules

Prefer state-machine logic over generic pseudocode when possible.

Primary artifacts:

- `notes/pseudocode/state_machines/*.md`
- `notes/pseudocode/modules/*.md`
- `notes/pseudocode/pseudotests/*.md`

---

## 5. Development Structure

Split implementation into:

- setup phase
- feature phase
- task plan

Each setup item is a standalone task.
Each feature is a standalone task.

Tasks should be:

- small
- explicit
- testable
- narrow enough for fast iteration

Target:

- 5-10 minute implementation chunks, excluding test runtime

For each task:

- document rationale
- document affected systems
- document canonical verification commands
- add/update tests
- update notes when implementation reveals new reality
- do not continue until the task is tested for the intended scope

Required supporting artifacts:

- `plan/setup/*.md`
- `plan/features/*.md`
- `plan/tasks/*.md`
- `plan/checklists/*.md`
- `notes/planning/implementation/*_decisions.md`
- `notes/logs/**/*.md`

---

## 6. Testing During Development

Testing happens continuously, but at the correct layer.

Use explicit layers:

- unit and bounded tests
- integration tests
- resilience/recovery tests
- performance tests
- real E2E tests

Rules:

- tests must cover all applicable systems, not just the convenient fast route
- bounded tests are required during initial implementation and review
- real E2E tests are required before a feature is complete
- tests are expected to be runnable in parallel; parallel-only failures indicate a defect in isolation, fixtures, or runtime resource ownership rather than an acceptable steady-state limitation
- explicit environment-capability gating is allowed, but shared-state serialization is not a valid long-term exception

If a feature is described as involving:

- database
- CLI
- daemon/backend
- YAML/config
- prompts

then the test strategy must explicitly account for those affected systems.

Primary checklist artifacts:

- `notes/catalogs/audit/auditability_checklist.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/audit/yaml_builtins_checklist.md`

---

## 7. Batch-Based Hardening During Development

Not all verification work should be done one feature at a time, and not all at once.

Some hardening should happen in dependency-ordered batches.

Use batches for areas where many features imply each other:

- command and migration consistency
- database-truth foundations
- core CLI/daemon surfaces
- compile/YAML/prompt contracts
- session/recovery/runtime coordination
- child scheduling/reconciliation/failure handling
- quality/docs/provenance/audit
- resilience hardening
- performance alignment

Why:

- many features share the same proving narrative
- many require the same harness/setup
- batching reduces duplicated work
- batching avoids unstable partial verification

Primary artifacts:

- `plan/update_tests/00_raise_existing_tests_to_doctrine_level.md`
- `plan/update_tests/01_batch_execution_groups.md`

---

## 8. After Development: Build Info

After the current planned implementation wave is complete, shift into build-info mode.

### Planned flow review

For pre-planned user flows/journeys:

- create a plan per flow
- run through the flow
- identify missing functionality
- identify broken behavior
- identify undocumented dependencies
- identify flows required by other flows that are still missing

### Real end-to-end

Run true E2E tasks from start to finish.

Requirements:

- set up the application from scratch
- run through every stage
- verify expected outcomes
- document failures
- do not simulate or skip important steps
- if a flow depends on real code, exercise real code

Primary artifacts:

- `notes/planning/implementation/per_flow_gap_remediation_plan.md`
- `notes/planning/implementation/full_real_end_to_end_flow_hardening_plan.md`
- `plan/e2e_tests/*.md`

---

## 9. Review Results

Take failures and gaps from flow review and E2E review and convert them into structured implementation work.

For each discovered issue:

- break it into a discrete feature/fix plan
- identify affected systems
- define invariants and failure mode
- define canonical verification commands
- define per-feature tests
- define batch membership if it belongs to a shared hardening wave

Rules:

- if a flow test fails, that is useful information
- do not weaken the flow just to get green tests
- fix or document the missing capability
- keep status labels honest:
  - implemented
  - verified
  - partial
  - flow_complete
  - release_ready

Primary artifacts:

- `plan/features/*.md`
- `plan/update_tests/*.md`
- `plan/e2e_tests/*.md`

---

## 10. Fix Stage

Execute the new plans generated from build-info and review-results.

Loop:

- run planned fixes starting from the next plan number
- complete and verify them
- return to build-info
- repeat until:
  - issues fixed
  - issues intentionally deferred and documented
  - critical flows pass
  - status claims are accurate

Logic:

- if `(issues fixed + issues remaining) != 0`, go back to Build Info
- use explicit exit criteria so the loop does not become endless polish

---

## 11. Release / Hardening Exit Criteria

A release or major hardening wave should only be considered complete when:

- critical flows pass with canonical commands
- known high-risk invariants are defended by tests
- all affected systems are exercised where applicable
- real E2E coverage exists for the intended feature set or is explicitly marked partial/deferred
- recovery behavior has been exercised where relevant
- performance-sensitive paths have been checked
- commands are consistent across README, notes, plans, checklists, and CI
- remaining limitations are explicitly documented

Primary artifacts:

- `plan/checklists/*.md`
- `notes/catalogs/audit/*.md`
- `plan/update_tests/*.md`
- `plan/e2e_tests/*.md`

---

## 12. Anti-Drift Rule

At virtually every stage, compare:

- design decisions
- implementation
- verification strategy
- status claims

against:

- the original brain-dump vision
- the notes/specs
- the current declared scope

If something drifted:

- fix it
- justify it
- document it

Do not allow:

- silent design drift
- silent narrowing of behavior
- silent change of proving commands
- silent omission of an affected system
- stale checklist/flow coverage claims
- artifact existence being mistaken for real verification

---

## Short Version

1. Define the vision and systems.
2. Define the architecture and invariants.
3. Define the features, flows, and proving commands.
4. Simulate expected and adversarial behavior before coding.
5. Implement in tiny tasks with tests and note updates.
6. Test across all affected systems, not just the fast path.
7. Harden in dependency-ordered batches where features share proving requirements.
8. Run planned flows and real E2E after development waves.
9. Turn failures into structured new plans.
10. Repeat until critical flows, invariants, and real-code verification are honestly complete.
