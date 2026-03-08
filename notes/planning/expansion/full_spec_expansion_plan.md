# Full Spec Expansion Plan

## Purpose

This document defines the next stage of work for the system: converting the current architecture and concept notes into a complete pseudocode-driven specification package.

The goal of this stage is not to implement the system yet. The goal is to make the system concrete enough that missing schemas, missing database constraints, missing runtime logic, and missing review/validation behavior become obvious before implementation begins.

This stage should produce enough detail that:

- every major behavior is defined in YAML or schema form
- every major state transition is persisted in the database design
- every major runtime path is written as basic pseudocode
- every major operator and AI-facing action has a CLI/introspection surface
- every original design goal can be traced to concrete spec artifacts

---

## Source Inputs

This plan is based on the current concept and revised spec set:

- `notes/explorations/original_concept.md`
- `notes/archive/superseded/yaml_schemas_spec_revised.md`
- `notes/archive/superseded/database_schema_spec_revised.md`
- `notes/archive/superseded/node_lifecycle_spec_revised.md`
- `notes/archive/superseded/runtime_command_loop_spec.md`
- `notes/archive/superseded/cli_surface_spec_revised.md`
- `notes/archive/superseded/git_rectification_spec_revised.md`

These documents define the architecture well, but they are still primarily design-level specs. They do not yet fully define the complete YAML inventory, the full database constraint model, the complete runtime pseudocode, or the full cross-spec traceability needed to detect gaps before implementation.

---

## Stage Goal

Produce a complete spec expansion package that turns the current system design into:

1. a canonical inventory of all required artifacts
2. a complete set of YAML schema families and default YAML files
3. a complete database schema catalog with constraints and indexes
4. a complete set of orchestration pseudocode flows
5. a traceability matrix from original goals to concrete spec artifacts
6. a review process for identifying contradictions and omissions
7. a v2 rewrite process for folding missing pieces back into the canonical specs
8. a repeatable review loop that continues until the design is closed enough for implementation slicing

---

## Core Principle

For every meaningful system behavior, the spec package should answer all of the following:

- What YAML defines it?
- What schema validates it?
- What database rows persist it?
- What CLI surfaces expose it?
- What pseudocode executes it?
- What validations and reviews gate it?
- What failure path exists for it?
- What recovery path exists for it?
- What rectification behavior applies to it?
- What audit trail exists for it later?

If any of those questions cannot be answered for a behavior, the design is incomplete.

---

## Deliverables

The output of this stage should include at minimum the following deliverables.

### 0. Major feature inventory and tracking model

The system should maintain a tracked list of major features/capabilities so the spec expansion effort can measure coverage against features, not just documents.

This inventory should be used during every review cycle.

Each feature should track:

- feature ID
- feature name
- feature description
- design-goal source
- related specs
- required YAML artifacts
- required DB artifacts
- required CLI artifacts
- required pseudocode artifacts
- dependencies on other features
- current status
- known gaps
- deferred questions

### 1. Canonical inventory

A master inventory document that maps:

- design goals
- runtime concepts
- YAML artifacts
- database artifacts
- CLI artifacts
- pseudocode artifacts
- status of completeness

### 2. Complete YAML inventory

The system should define all schema families as concrete v2 schemas and define all default YAML documents required by the default ladder and runtime.

This includes:

- node definition schemas
- task definition schemas
- subtask definition schemas
- validation check schemas
- output definition schemas
- layout definition schemas
- hook definition schemas
- override definition schemas
- review definition schemas
- testing definition schemas
- documentation generation definition schemas
- session/runtime-related YAML definitions where applicable
- rectification/rebuild-related YAML definitions where applicable

### 3. Default YAML file library

The system should have concrete default YAML files written for the default node kinds and flows.

This includes:

- default node kinds
- default tasks per node kind
- default subtasks per task
- default layout files
- default hook files
- default validation files
- default review files
- default testing files
- default documentation files
- default rectify/rebuild task files

### 4. Complete database catalog

The PostgreSQL spec should be expanded from structure-level design into migration-grade design detail.

This includes:

- all tables
- all columns
- all foreign keys
- all primary keys
- all unique constraints
- all non-null rules
- all enum domains or check constraints
- all indexes
- all cascade/restrict behaviors
- all views and current-state views
- all audit/history tables
- all integrity assumptions that must be enforced in application logic if not representable directly in SQL

### 5. Runtime pseudocode package

Every major system path should be described in basic pseudocode.

This includes:

- node creation
- node version supersession
- workflow compilation
- override resolution
- hook expansion
- task compilation
- subtask compilation
- run admission
- dependency admission checks
- AI session bootstrap
- canonical subtask execution loop
- validation execution
- review execution
- testing execution
- pause/gating logic
- child session push/pop logic
- child node spawning logic
- wait-on-child logic
- wait-on-sibling logic
- merge ordering logic
- finalize logic
- regenerate-subtree logic
- rectify-upstream logic
- session recovery logic
- idle detection and nudge logic
- docs generation logic
- provenance extraction/update logic

### 6. Gap matrix

A formal gap matrix should be produced for the whole system.

Each major goal or behavior should be classified as:

- covered
- partially covered
- missing
- contradictory
- underspecified
- requires new YAML schema
- requires new database constraint
- requires new runtime pseudocode
- requires new CLI surface

### 7. V2 canonical spec rewrite

Once the missing pieces are identified, the existing specs should be rewritten into v2 versions that fold in the missing detail and resolve contradictions.

### 8. Iterative closure review

After v2 rewrite, another review pass should be run to check whether all behaviors are now fully covered. If not, the process repeats until the system is sufficiently closed for implementation planning.

---

## Recommended Phases

## Phase A: Canonical Inventory And Traceability

### Objective

Create a master inventory of what the system must define and what is already defined.

### Outputs

- a traceability matrix linking original design goals to specs
- a feature inventory and tracking table
- a concept inventory of all runtime entities
- a coverage matrix across YAML, DB, CLI, and pseudocode surfaces

### Required work

- extract all major design goals from `notes/explorations/original_concept.md`
- extract all major features/capabilities from the concept and revised specs
- extract all currently defined entities from the revised specs
- list all defined and implied concepts
- identify where multiple specs refer to the same concept using different wording
- normalize terminology into one canonical vocabulary
- assign stable feature IDs and define initial feature status values

### Key questions

- Are all major concepts named consistently?
- Are any concepts present in runtime docs but absent from schemas?
- Are any concepts present in DB docs but absent from runtime behavior?
- Are any concepts present in the concept note but missing everywhere else?

### Exit criteria

- there is one canonical vocabulary
- there is one tracked feature inventory
- every major concept is listed
- every design goal is mapped to at least one spec area

---

## Major Feature Inventory

The following major features should be tracked explicitly during the spec expansion process.

These are not implementation tickets yet. They are feature-level capability buckets used to verify the architecture is complete.

### F01. Configurable node hierarchy

Support configurable tiers and node kinds rather than hardcoding `epic -> phase -> plan -> task`.

### F02. Node versioning and supersession

Support durable node versions, regeneration via superseding versions, and lineage across rebuilds.

### F03. Immutable workflow compilation

Compile mutable YAML plus overrides and hooks into immutable workflow snapshots used for execution and history.

### F04. YAML schema system

Define and validate all schema families required for nodes, tasks, subtasks, layouts, hooks, validation, outputs, and related artifacts.

### F05. Default YAML library

Provide concrete default YAML definitions for the default ladder, task catalog, subtask catalog, hooks, validation, review, testing, and rectification flows.

### F06. Override and merge resolution

Support project-local overrides, deterministic merge behavior, and source lineage for resolved YAML.

### F07. Durable node lifecycle state

Persist node lifecycle states and execution states with resumable runtime cursors.

### F08. Dependency graph and admission control

Support child and sibling dependencies, dependency validation, dependency waiting, and run admission enforcement.

### F09. Node run orchestration

Support node runs, task/subtask execution, retry behavior, pause behavior, and completion/failure handling.

### F10. AI-facing CLI command loop

Provide a CLI that AI sessions use directly for prompts, context retrieval, progress updates, summaries, and workflow advancement.

### F11. Operator CLI and introspection

Provide a broad CLI surface for operators to inspect hierarchy, runs, workflows, prompts, sessions, summaries, dependencies, merges, docs, and provenance.

### F12. Session binding and resume

Support primary session binding, durable session tracking, tmux integration, resume behavior, and reattachment behavior.

### F13. Idle detection and nudge behavior

Detect idle sessions, reissue current work context, and support stuck-session recovery without corrupting cursor state.

### F14. Optional pushed child sessions

Support bounded research/review/verification child sessions for context isolation without transferring node ownership.

### F15. Child node spawning

Support creating and running child nodes from layouts with dependency-aware scheduling and durable lineage.

### F16. Manual tree construction

Allow users to manually define node trees instead of relying only on automatic decomposition.

### F17. Deterministic branch model

Define deterministic branch identity, seed/final commit tracking, and branch generation metadata.

### F18. Child merge and reconcile pipeline

Support deterministic child merge ordering, reconcile subtasks, and parent reconstruction from seed plus child finals.

### F19. Regeneration and upstream rectification

Support subtree regeneration, ancestor rebuilds, and selective reuse of current sibling outputs.

### F20. Conflict detection and conflict resolution

Track merge conflicts durably and support structured conflict handling within rectification flows.

### F21. Validation framework

Support declarative validation checks, validation execution, validation result persistence, and validation gating.

### F22. Review framework

Support review subtasks, review outputs, review gating, and review before finalization where policy requires it.

### F23. Testing framework integration

Support project-defined testing hooks, test execution gates, and test result integration into node completion.

### F24. User gating and pause flags

Support pause points, user approval gates, pause summaries, and manual continuation points.

### F25. Failure escalation and parent decision logic

Support structured failure summaries, parent-only escalation, retry thresholds, and user deferment behavior.

### F26. Hook system

Support policy-driven hook insertion across node, task, subtask, validation, testing, review, and merge lifecycle points.

### F27. Source document lineage

Track all source YAML, overrides, hashes, and roles that contributed to compiled workflows.

### F28. Prompt history and summary history

Persist prompts, summaries, and prompt/summary lineage for auditability and introspection.

### F29. Documentation generation

Support local and merged documentation views generated from static analysis plus relational/rationale data.

### F30. Code provenance and rationale mapping

Track entities, entity changes, relations, and rationale linking code changes back to nodes and prompts.

### F31. Daemon authority and durable orchestration record

Ensure the daemon owns live orchestration while all important operational state remains queryable and recoverable from durable storage.

### F32. Automation of all user-visible actions

Ensure everything the user can do in the interface has an automatable CLI/runtime path and audit trail.

### F33. Optional isolated runtime environments

Support optional isolated containers/namespaces for child work that requires environmental separation.

### F34. Provider-agnostic session recovery

Support resume behavior even when provider session identity is partial or provider-specific behavior differs.

### F35. Project policy extensibility

Allow projects to redefine ladders, policies, hooks, and quality gates through YAML and override mechanisms.

### F36. Auditable history and reproducibility

Ensure node state, workflow state, git state, prompts, summaries, merge lineage, and rebuild events are reproducible and inspectable later.

---

## Feature Tracking Model

Major features should be tracked in a dedicated document or table during the spec expansion stage.

Recommended statuses:

- `identified`
- `in_specification`
- `specified`
- `needs_review`
- `gap_found`
- `revising`
- `accepted`
- `deferred`

Recommended tracking columns:

- feature ID
- feature name
- status
- priority
- source design goals
- spec documents
- YAML artifacts
- DB artifacts
- CLI artifacts
- pseudocode artifacts
- dependencies
- open questions
- known gaps
- review notes

Recommended review use:

- every review cycle should assess feature coverage, not just document completion
- every gap should be attached to one or more feature IDs
- every new schema, DB change, or pseudocode module should reference feature IDs

---

## Phase B: YAML Concretization

### Objective

Turn the schema discussions into actual full schema and default YAML artifact inventories.

### Outputs

- complete schema family definitions
- complete default YAML file list
- complete default node/task/subtask library
- example YAML instances for all core flows

### Required work

- define every root schema family concretely
- define required and optional fields for each family
- define reusable field fragments where appropriate
- define merge/override rules with examples
- define actual default node kinds and their default tasks
- define actual default tasks and their subtasks
- define actual default hooks and hook insertion behavior
- define actual default layout files

### Required artifact inventory

At minimum, inventory the following:

- node definition YAMLs
- task definition YAMLs
- subtask definition YAMLs
- layout YAMLs
- hook YAMLs
- validation YAMLs
- review YAMLs
- testing YAMLs
- doc-build YAMLs
- rectify/rebuild YAMLs
- override YAMLs
- project policy YAMLs

### Key questions

- What YAML families are still only implied?
- What default YAML files are required for the default ladder to run end to end?
- Which YAMLs are generic framework files versus project-local overrides?
- What pieces must be compiled into immutable workflow snapshots?

### Exit criteria

- every runtime behavior maps to YAML or an explicit decision that it is code-only
- every default node kind has concrete YAML
- every default task and subtask has a home in YAML

---

## Phase C: Database Concretization

### Objective

Expand the database design into a stricter, implementation-grade schema specification.

### Outputs

- a full database catalog
- explicit check constraints and enum/domain decisions
- explicit indexing strategy
- explicit current-state and history views
- explicit application-enforced integrity rules

### Required work

- review each table and all implied relations
- define allowed status values and lifecycle values
- define where to use text plus check constraint versus reference table versus enum/domain
- define uniqueness boundaries
- define indexing requirements for runtime and CLI queries
- define deletion policy and cascade/restrict rules
- define which integrity rules cannot be captured directly in SQL

### Areas likely needing more detail

- lifecycle state constraints
- run state constraints
- child failure thresholds
- dependency validity rules
- session ownership rules
- supersession constraints
- merge event ordering constraints
- provenance table uniqueness/identity rules

### Key questions

- What states are legal for each table?
- What transitions are legal or illegal?
- What fields must never be nullable in active rows?
- What runtime assumptions need explicit DB support?

### Exit criteria

- the schema is detailed enough to write migrations from it
- the runtime can be explained against persisted tables without hidden in-memory assumptions

---

## Phase D: Runtime Pseudocode Expansion

### Objective

Write end-to-end basic pseudocode for every major orchestration path.

### Outputs

- a pseudocode module or section for each major flow
- decision trees for failure handling and pause behavior
- dependency-resolution logic
- regeneration and upstream rebuild algorithms

### Required work

- write pseudocode for the happy path
- write pseudocode for failure paths
- write pseudocode for user-gated paths
- write pseudocode for recovery/resume paths
- write pseudocode for regeneration paths
- write pseudocode for review/validation/testing integration

### Required pseudocode modules

- `create_node_version(...)`
- `compile_workflow(...)`
- `resolve_overrides(...)`
- `expand_hooks(...)`
- `admit_node_run(...)`
- `bind_session(...)`
- `run_node_loop(...)`
- `execute_subtask(...)`
- `run_validation_checks(...)`
- `run_review(...)`
- `run_testing(...)`
- `pause_for_user(...)`
- `spawn_child_node(...)`
- `push_child_session(...)`
- `pop_child_session(...)`
- `wait_for_dependencies(...)`
- `finalize_node(...)`
- `regenerate_node_and_descendants(...)`
- `rectify_upstream(...)`
- `recover_interrupted_run(...)`
- `nudge_idle_session(...)`
- `build_docs(...)`
- `update_provenance(...)`

### Key questions

- Is every CLI operation backed by a real algorithm?
- Does every persisted state have a producer and consumer?
- Are there any state transitions with no explicit owner?
- Are retries, escalations, and pauses deterministic?

### Exit criteria

- every major flow has a pseudocode path
- failure and recovery paths exist for all critical flows
- there are no major orchestration behaviors left implied

---

## Phase E: Cross-Spec Consistency Review

### Objective

Review all YAML, DB, CLI, runtime, and git behavior together and expose contradictions.

### Outputs

- a consistency review report
- a contradiction list
- a missing-artifact list
- a prioritization list for fixes

### Required work

- compare YAML concepts to DB persistence design
- compare DB persistence design to CLI queryability
- compare CLI commands to runtime pseudocode ownership
- compare runtime behavior to git rectification behavior
- compare all of the above to original design goals

### Consistency checks

- every compiled concept has a DB home
- every DB concept has a CLI read path if operationally relevant
- every CLI mutation path has runtime pseudocode
- every node lifecycle transition is represented consistently
- every rebuild/merge behavior is represented consistently
- every review/validation/testing path is represented consistently

### Exit criteria

- contradictions are documented
- missing pieces are categorized
- next changes for v2 rewrite are explicit

---

## Phase F: V2 Canonical Spec Rewrite

### Objective

Rewrite the current design notes into v2 specs that incorporate the missing detail discovered in prior phases.

### Outputs

- v2 YAML schema spec
- v2 database schema spec
- v2 node lifecycle spec
- v2 runtime command loop spec
- v2 CLI surface spec
- v2 git rectification spec
- any new specs needed for review/testing/docs/provenance if those deserve separate documents

### Required work

- integrate resolved terminology
- integrate new schema families
- integrate missing DB constraints
- integrate missing pseudocode-derived rules
- integrate newly required CLI surfaces
- remove contradictions across docs

### Exit criteria

- the v2 docs can serve as canonical implementation references
- missing behavior is either resolved or explicitly deferred

---

## Phase G: Closure Review And Implementation Slicing

### Objective

Confirm that the spec package is complete enough to begin implementation planning.

### Outputs

- a final review report
- a list of remaining open questions
- an implementation slice plan grouped by risk and dependency

### Required work

- rerun the gap matrix against the v2 docs
- verify that all design goals have traceability
- verify that all major behaviors have YAML, DB, CLI, and pseudocode coverage
- identify the remaining ambiguous or optional areas
- split implementation into phases only after spec closure is acceptable

### Exit criteria

- the design is closed enough for implementation work
- the remaining open items are intentional, bounded, and documented

---

## Immediate Gaps Already Visible

Based on the current docs, the following appear to be the largest present gaps.

### 1. The full default YAML library is not yet written

The schema families are described, but the complete default file set for node kinds, tasks, subtasks, hooks, validation, review, testing, and rectify flows is not yet present.

### 2. The database model still needs stronger constraint design

The tables are strong conceptually, but many enum/value constraints, uniqueness assumptions, index requirements, and integrity boundaries still need to be made explicit.

### 3. Several runtime branch paths are still implied rather than written

The canonical loop exists, but a full system-level pseudocode package for retries, user gating, dependency waits, conflict reconciliation, and failure escalation is still missing.

### 4. Hook, validation, review, testing, and finalize ordering needs one canonical rule

The behavior is discussed in multiple places, but one authoritative ordering and ownership model still needs to be frozen.

### 5. Override and merge semantics need more concrete examples

The resolution order is defined, but conflict examples and override edge cases still need to be written out.

### 6. Provenance and documentation generation need more operational detail

The database includes provenance and docs concepts, but the actual extraction, refresh, merge-scope, and rebuild logic still needs explicit pseudocode.

### 7. The “everything user-can-do is automatable” goal needs a full action matrix

This should map UI/operator actions to CLI commands, DB mutations, runtime owners, and audit trails.

### 8. Parent-side failure decision logic needs a full algorithm

Failure escalation is defined conceptually, but the parent decision tree for retry, local replan, upstream rectification, or user deferment should be written explicitly.

---

## Working Method

The recommended method for this stage is:

1. inventory everything already defined
2. normalize terminology
3. enumerate every missing artifact
4. write the missing YAML/schema/database/pseudocode artifacts
5. run a structured review against original goals
6. revise the canonical specs into v2
7. rerun the review
8. repeat until coverage is good enough for implementation slicing

This should be treated as a deliberate rinse-and-repeat process, not a one-pass documentation exercise.

---

## Review Checklist

Use the following checklist during each review pass.

### Design goal coverage

- Is each original design goal represented?
- Is each goal mapped to concrete artifacts?
- Is any goal partially implemented only in prose?

### YAML coverage

- Does every major behavior have YAML ownership or an explicit exception?
- Are all required schema families defined?
- Are all default node/task/subtask files defined?

### Database coverage

- Is every important state persisted?
- Are constraints and uniqueness rules explicit?
- Are current-state and history access patterns supported?

### Runtime coverage

- Does every lifecycle transition have an owner?
- Does every failure path have a handler?
- Does every resume/recovery path have pseudocode?

### CLI coverage

- Can every operationally relevant durable concept be queried?
- Are mutation commands limited to safe and necessary actions?
- Is AI-session execution fully supportable through CLI?

### Git/rectification coverage

- Can every rebuild be reproduced from seed plus current child finals?
- Are merge order and conflict handling deterministic?
- Are merge events and rebuild events fully auditable?

### Review/validation/testing coverage

- Are all gates represented consistently?
- Is their order canonical?
- Are pass/fail consequences explicit?

### Provenance/docs coverage

- Can code changes be tied back to node history and rationale?
- Are local and merged doc views modeled clearly?
- Is provenance generation tied to rebuild and merge flows?

---

## Iteration Exit Criteria

This spec expansion stage should only be considered complete when, for every major feature or behavior, the answer is known for all of the following:

- defining YAML
- validating schema
- persisted database state
- CLI inspection path
- runtime pseudocode
- failure handling
- recovery handling
- review/validation/testing gating
- regeneration behavior
- auditability

If any major feature is missing one of those, the loop continues.

---

## What Comes After This Stage

Only after this stage is sufficiently complete should the work move into implementation slicing.

At that point, implementation planning should be based on:

- stable v2 specs
- explicit artifact inventories
- clear runtime pseudocode
- known DB constraints
- known review/validation/testing gates
- known risk areas and open questions

Implementation phases should then be organized around dependency order and risk reduction, rather than around vague feature labels.

---

## Recommended Next Document Set

The next documents to create after this plan are:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/inventory/yaml_inventory_v2.md`
- `notes/catalogs/inventory/default_yaml_library_plan.md`
- `notes/planning/expansion/database_schema_v2_expansion.md`
- `notes/planning/expansion/runtime_pseudocode_plan.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`

These can later be folded into the canonical v2 specs once the review cycles converge.
