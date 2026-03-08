# Major Feature Inventory

## Purpose

This document is the tracked inventory of major system features/capabilities for the AI coding system rewrite.

These features are not implementation tickets. They are architecture-level capability buckets used to:

- track what the system must support
- map design goals to concrete specs
- identify missing YAML, DB, CLI, and pseudocode artifacts
- drive review and gap analysis
- anchor later implementation slicing

This document should be updated during every major review cycle.

---

## Status Model

Recommended feature statuses:

- `identified`
- `in_specification`
- `specified`
- `needs_review`
- `gap_found`
- `revising`
- `accepted`
- `deferred`

This document has now progressed beyond initial identification. Many features are now either:

- `specified`
- `needs_review`
- `deferred`

The goal of future updates is to keep statuses aligned with the canonical v2 specs and the remaining true open gaps.

---

## Tracking Fields

Each feature should eventually track:

- feature ID
- feature name
- status
- priority
- prompt coverage
- description
- source design goals
- related specs
- required YAML artifacts
- required DB artifacts
- required CLI artifacts
- required pseudocode artifacts
- dependencies
- known gaps
- open questions
- review notes

---

## Feature Table

| ID | Feature | Status | Priority | Prompts | Description | Depends On |
| --- | --- | --- | --- | --- | --- | --- |
| F01 | Configurable node hierarchy | specified | critical |  | Support configurable tiers and node kinds rather than hardcoded `epic -> phase -> plan -> task`. | |
| F02 | Node versioning and supersession | needs_review | critical |  | Support durable node versions, regeneration via superseding versions, and lineage across rebuilds. | F01 |
| F03 | Immutable workflow compilation | needs_review | critical |  | Compile YAML, overrides, and hooks into immutable workflow snapshots used for execution and history. | F01, F02, F04, F06, F26, F27 |
| F04 | YAML schema system | specified | critical |  | Define and validate all schema families required for runtime configuration. | F01 |
| F05 | Default YAML library | needs_review | high | x | Provide concrete default YAML files for node kinds, tasks, subtasks, hooks, validation, review, testing, rectification, and prompt assets. | F04 |
| F06 | Override and merge resolution | needs_review | high |  | Support project-local overrides, deterministic merge behavior, and resolved YAML lineage. | F04, F27, F35 |
| F07 | Durable node lifecycle state | specified | critical |  | Persist node lifecycle and execution state with resumable runtime cursors. | F02, F03, F31 |
| F08 | Dependency graph and admission control | needs_review | critical |  | Support child/sibling dependencies, dependency validation, admission checks, and wait states. | F01, F02, F07 |
| F09 | Node run orchestration | specified | critical | x | Support task/subtask execution, retries, pauses, completion, and failure handling for node runs. | F03, F07, F08, F10 |
| F10 | AI-facing CLI command loop | specified | critical | x | Provide the CLI loop used by AI sessions for prompts, context, progress, summaries, and advancement. | F07, F09, F11 |
| F11 | Operator CLI and introspection | specified | critical |  | Expose hierarchy, runs, workflows, prompts, sessions, dependencies, merges, docs, and provenance through CLI. | F31, F36 |
| F12 | Session binding and resume | resolved_in_principle | critical |  | Support primary session binding, durable session tracking, tmux integration, resume behavior, and reattachment. | F07, F09, F31, F34 |
| F13 | Idle detection and nudge behavior | needs_review | medium | x | Detect idle sessions and reissue work context without corrupting execution state. | F10, F12 |
| F14 | Optional pushed child sessions | needs_review | medium | x | Support bounded research/review/verification child sessions for context isolation. | F10, F12 |
| F15 | Child node spawning | needs_review | high | x | Support creating and running child nodes from layouts with durable lineage and dependency-aware scheduling. | F01, F02, F03, F08 |
| F16 | Manual tree construction | needs_review | medium |  | Allow users to define node trees manually rather than only through automatic decomposition. | F01, F15 |
| F17 | Deterministic branch model | needs_review | critical |  | Define deterministic branch identity, seed/final commit tracking, and branch generation metadata. | F02, F36 |
| F18 | Child merge and reconcile pipeline | specified | critical | x | Support deterministic child merge ordering, reconcile subtasks, and parent reconstruction from seed plus child finals. | F15, F17, F19, F20 |
| F19 | Regeneration and upstream rectification | needs_review | critical | x | Support subtree regeneration, ancestor rebuilds, and selective reuse of current sibling outputs. | F02, F17, F18 |
| F20 | Conflict detection and resolution | specified | high |  | Track merge conflicts durably and support structured conflict handling during rebuilds. | F18, F19 |
| F21 | Validation framework | specified | critical | x | Support declarative validation checks, validation execution, persistence, and gating. | F04, F09 |
| F22 | Review framework | specified | high | x | Support review subtasks, review outputs, review gating, and review before finalization where required. | F04, F09 |
| F23 | Testing framework integration | specified | high | x | Support project-defined testing hooks and test result integration into node completion. | F21, F26, F35 |
| F24 | User gating and pause flags | specified | high | x | Support pause points, approval gates, pause summaries, and manual continuation points. | F09, F10, F21, F22 |
| F25 | Failure escalation and parent decision logic | resolved_in_principle | critical | x | Support structured failure summaries, parent-only escalation, retry thresholds, and user deferment behavior. | F08, F09, F24 |
| F26 | Hook system | needs_review | high |  | Support policy-driven hook insertion across lifecycle points. | F04, F35 |
| F27 | Source document lineage | needs_review | high |  | Track all source YAML, overrides, hashes, and roles that contributed to compiled workflows. | F04, F06, F31, F36 |
| F28 | Prompt history and summary history | needs_review | medium | x | Persist prompts, summaries, prompt-template identity, and prompt/summary lineage for auditability and introspection. | F09, F11, F31, F36 |
| F29 | Documentation generation | specified | medium | x | Support local and merged documentation views generated from code and rationale data. | F18, F30, F36 |
| F30 | Code provenance and rationale mapping | resolved_in_principle | high |  | Track entities, entity changes, relations, and rationale linking code changes back to nodes and prompts. | F02, F11, F31, F36 |
| F31 | Daemon authority and durable orchestration record | specified | critical |  | Ensure the daemon owns live orchestration while all critical operational state is durably queryable and recoverable from the database. | |
| F32 | Automation of all user-visible actions | resolved_in_principle | high |  | Ensure all user-visible actions have an automatable CLI/runtime path and audit trail. | F10, F11, F31 |
| F33 | Optional isolated runtime environments | deferred | medium |  | Support optional isolated containers/namespaces for work requiring environmental separation. | F14, F15, F35 |
| F34 | Provider-agnostic session recovery | resolved_in_principle | medium | x | Support resume behavior even when provider session identity differs or is partially available. | F12 |
| F35 | Project policy extensibility | needs_review | high | x | Allow projects to redefine ladders, policies, hooks, quality gates, and prompt packs through YAML and overrides. | F01, F04, F06 |
| F36 | Auditable history and reproducibility | specified | critical | x | Ensure node state, workflow state, git state, prompts, merges, and rebuild events are reproducible and inspectable later. | F02, F03, F17, F27, F28, F31 |

`Prompts` is checked when the default system should ship authored prompt assets or runtime-generated prompt payloads for that feature.

---

## Current Review Snapshot

The feature set now broadly falls into these buckets:

- `specified`: the feature has a solid spec-level definition in the v2 docs
- `resolved_in_principle`: the feature has a dedicated appendix or strong design answer, but still needs implementation-grade folding back into the canonical docs
- `needs_review`: the feature is mostly designed, but one or more meaningful design details still need a final pass
- `deferred`: intentionally not on the first implementation critical path

The largest remaining `needs_review` areas are:

- child spawning and scheduling
- dependency validation and authority resolution
- branch naming and cutover-adjacent details
- hook expansion
- source-role and summary taxonomy normalization
- manual vs automatic tree coexistence

---

## Feature Details

## F01. Configurable node hierarchy

- Status: `identified`
- Priority: `critical`
- Description: The runtime must support configurable tiers and node kinds instead of hardcoding one ladder.
- Source design goals:
  - configurable concept levels
  - user-defined hierarchy semantics
- Related specs:
  - `notes/original_concept.md`
  - `notes/yaml_schemas_spec_revised.md`
  - `notes/node_lifecycle_spec_revised.md`
- Expected artifacts:
  - YAML schema support for `tier` and `kind`
  - DB support for flexible tiers and kinds
  - runtime rules for parent/child constraints
- Known gaps:
  - parent/child constraint schema is still not fully written
  - default ladder versus custom ladder rules need sharper boundaries

## F02. Node versioning and supersession

- Status: `identified`
- Priority: `critical`
- Description: Nodes must be versioned durably rather than mutated in place.
- Source design goals:
  - rebuild from prompts/spec changes
  - preserve lineage across regeneration
- Related specs:
  - `notes/database_schema_spec_revised.md`
  - `notes/node_lifecycle_spec_revised.md`
  - `notes/git_rectification_spec_revised.md`
- Expected artifacts:
  - `node_versions`
  - `rebuild_events`
  - supersession pseudocode
- Known gaps:
  - lifecycle handling of superseded active runs needs explicit rules
  - descendant supersession policy needs exact pseudocode

## F03. Immutable workflow compilation

- Status: `identified`
- Priority: `critical`
- Description: Execution must run from compiled immutable workflow snapshots rather than mutable YAML.
- Source design goals:
  - reproducibility
  - safe resume
  - auditability
- Related specs:
  - `notes/yaml_schemas_spec_revised.md`
  - `notes/database_schema_spec_revised.md`
  - `notes/node_lifecycle_spec_revised.md`
- Expected artifacts:
  - compiled workflow schema
  - source lineage DB tables
  - compile pseudocode
- Known gaps:
  - full hook-expansion algorithm needs writing
  - compilation error handling needs fuller pseudocode

## F04. YAML schema system

- Status: `identified`
- Priority: `critical`
- Description: All generated YAML must be validated against explicit schema families.
- Related specs:
  - `notes/yaml_schemas_spec_revised.md`
- Expected artifacts:
  - full schema inventory
  - field-level constraints
  - sample valid/invalid documents
- Known gaps:
  - some schema families are still implied rather than enumerated

## F05. Default YAML library

- Status: `identified`
- Priority: `high`
- Description: The system needs actual default YAML files, not just schema definitions.
- Related specs:
  - `notes/yaml_schemas_spec_revised.md`
  - `notes/original_concept.md`
- Expected artifacts:
  - default node YAMLs
  - default task YAMLs
  - default subtask YAMLs
  - default hooks/review/validation/testing YAMLs
- Known gaps:
  - the concrete file inventory has not yet been written

## F06. Override and merge resolution

- Status: `identified`
- Priority: `high`
- Description: Project-local overrides must merge deterministically and preserve source lineage.
- Related specs:
  - `notes/yaml_schemas_spec_revised.md`
  - `notes/database_schema_spec_revised.md`
- Expected artifacts:
  - override schema
  - merge precedence rules
  - lineage capture in compiled workflow
- Known gaps:
  - conflict examples and edge cases are still missing

## F07. Durable node lifecycle state

- Status: `identified`
- Priority: `critical`
- Description: Lifecycle state and run state must be durably persisted and queryable.
- Related specs:
  - `notes/node_lifecycle_spec_revised.md`
  - `notes/database_schema_spec_revised.md`
- Expected artifacts:
  - lifecycle state value catalog
  - transition rules
  - DB constraints and views
- Known gaps:
  - legal transition enforcement still needs clearer ownership

## F08. Dependency graph and admission control

- Status: `identified`
- Priority: `critical`
- Description: Nodes and subtasks must enforce child and sibling dependency readiness.
- Related specs:
  - `notes/node_lifecycle_spec_revised.md`
  - `notes/database_schema_spec_revised.md`
- Expected artifacts:
  - dependency DB tables
  - runtime wait/admission pseudocode
  - CLI dependency views
- Known gaps:
  - dependency validation rules for invalid graph shapes need writing

## F09. Node run orchestration

- Status: `identified`
- Priority: `critical`
- Description: Node runs need explicit ownership of task and subtask progression, retries, pauses, and completion.
- Related specs:
  - `notes/node_lifecycle_spec_revised.md`
  - `notes/runtime_command_loop_spec.md`
- Expected artifacts:
  - subtask loop pseudocode
  - retry policy behavior
  - completion/failure rules
- Known gaps:
  - some pause and escalation branches are still only implied

## F10. AI-facing CLI command loop

- Status: `identified`
- Priority: `critical`
- Description: AI sessions should use CLI commands for all runtime interactions.
- Related specs:
  - `notes/runtime_command_loop_spec.md`
  - `notes/cli_surface_spec_revised.md`
- Expected artifacts:
  - canonical AI loop command set
  - command-to-DB mapping
  - pseudocode ownership
- Known gaps:
  - some command semantics still need strict mutation rules

## F11. Operator CLI and introspection

- Status: `identified`
- Priority: `critical`
- Description: Operators need broad read access to all durable state and safe mutation access where appropriate.
- Related specs:
  - `notes/cli_surface_spec_revised.md`
- Expected artifacts:
  - command catalog
  - read/mutate split
  - DB query mappings
- Known gaps:
  - some operational views likely still need explicit query definitions

## F12. Session binding and resume

- Status: `identified`
- Priority: `critical`
- Description: Node runs should bind to primary sessions and support resume after interruption.
- Related specs:
  - `notes/runtime_command_loop_spec.md`
  - `notes/database_schema_spec_revised.md`
- Expected artifacts:
  - session tables
  - bind/resume pseudocode
  - recovery decision rules
- Known gaps:
  - recovery when tmux and provider state disagree needs fuller rules

## F13. Idle detection and nudge behavior

- Status: `identified`
- Priority: `medium`
- Description: The system should detect idle sessions and reissue current task context safely.
- Related specs:
  - `notes/runtime_command_loop_spec.md`
- Expected artifacts:
  - heartbeat semantics
  - stale-session thresholds
  - nudge pseudocode
- Known gaps:
  - threshold and escalation policy are not yet concrete

## F14. Optional pushed child sessions

- Status: `identified`
- Priority: `medium`
- Description: Context-isolated child sessions should support research/review work without taking node ownership.
- Related specs:
  - `notes/runtime_command_loop_spec.md`
  - `notes/cli_surface_spec_revised.md`
- Expected artifacts:
  - child session lifecycle
  - session push/pop CLI
  - summary handoff logic
- Known gaps:
  - parent context snapshot and merge-back rules need more detail

## F15. Child node spawning

- Status: `identified`
- Priority: `high`
- Description: Layouts should create child nodes durably with dependencies and scheduling metadata.
- Related specs:
  - `notes/original_concept.md`
  - `notes/yaml_schemas_spec_revised.md`
  - `notes/node_lifecycle_spec_revised.md`
- Expected artifacts:
  - layout YAML
  - child creation pseudocode
  - child lineage persistence
- Known gaps:
  - exact scheduling admission rules for independent children still need detail

## F16. Manual tree construction

- Status: `identified`
- Priority: `medium`
- Description: Users should be able to manually define node trees at any layer.
- Related specs:
  - `notes/original_concept.md`
  - `notes/node_lifecycle_spec_revised.md`
- Expected artifacts:
  - manual creation CLI/API paths
  - YAML examples
  - validation rules
- Known gaps:
  - constraints around partially manual and partially automatic trees need clarification

## F17. Deterministic branch model

- Status: `identified`
- Priority: `critical`
- Description: Branch naming and git metadata must be deterministic and auditable.
- Related specs:
  - `notes/git_rectification_spec_revised.md`
- Expected artifacts:
  - branch naming rules
  - seed/final/head persistence
  - generation metadata
- Known gaps:
  - exact naming spec should be frozen in one canonical place

## F18. Child merge and reconcile pipeline

- Status: `identified`
- Priority: `critical`
- Description: Parent nodes reconstruct themselves by resetting to seed and merging child finals in deterministic order.
- Related specs:
  - `notes/git_rectification_spec_revised.md`
- Expected artifacts:
  - merge-order logic
  - reconcile task YAML
  - merge event persistence
- Known gaps:
  - reconcile algorithm detail is still high-level

## F19. Regeneration and upstream rectification

- Status: `identified`
- Priority: `critical`
- Description: Changed nodes should trigger subtree regeneration and upstream rebuilds using current sibling finals.
- Related specs:
  - `notes/git_rectification_spec_revised.md`
  - `notes/node_lifecycle_spec_revised.md`
- Expected artifacts:
  - supersession algorithm
  - subtree regeneration pseudocode
  - upstream rebuild pseudocode
- Known gaps:
  - rebuild concurrency rules and cutover timing need detail

## F20. Conflict detection and resolution

- Status: `identified`
- Priority: `high`
- Description: Merge conflicts must be tracked durably and resolved through structured reconcile behavior.
- Related specs:
  - `notes/git_rectification_spec_revised.md`
  - `notes/database_schema_spec_revised.md`
- Expected artifacts:
  - conflict event tables
  - conflict-handling pseudocode
  - reconcile subtasks
- Known gaps:
  - multi-conflict retry policy still needs explicit design

## F21. Validation framework

- Status: `identified`
- Priority: `critical`
- Description: Validation should be declarative, executable, persistent, and gate completion.
- Related specs:
  - `notes/yaml_schemas_spec_revised.md`
  - `notes/node_lifecycle_spec_revised.md`
- Expected artifacts:
  - validation schema
  - validation results persistence
  - validation CLI surfaces
- Known gaps:
  - validation result model needs more detailed shape

## F22. Review framework

- Status: `identified`
- Priority: `high`
- Description: Review should be an explicit stage with persistent outputs and gating effects.
- Related specs:
  - `notes/yaml_schemas_spec_revised.md`
  - `notes/node_lifecycle_spec_revised.md`
- Expected artifacts:
  - review task/subtask YAML
  - review output persistence
  - review decision logic
- Known gaps:
  - review output schema and pass/fail implications need more structure

## F23. Testing framework integration

- Status: `identified`
- Priority: `high`
- Description: Projects should be able to enforce testing through hooks and gates.
- Related specs:
  - `notes/original_concept.md`
  - `notes/yaml_schemas_spec_revised.md`
- Expected artifacts:
  - testing hooks
  - test result persistence
  - testing gate rules
- Known gaps:
  - dedicated testing spec may be needed

## F24. User gating and pause flags

- Status: `identified`
- Priority: `high`
- Description: The runtime should support pause conditions that require user review or approval.
- Related specs:
  - `notes/yaml_schemas_spec_revised.md`
  - `notes/git_rectification_spec_revised.md`
  - `notes/node_lifecycle_spec_revised.md`
- Expected artifacts:
  - pause flag model
  - summary prompts
  - approval CLI
- Known gaps:
  - multiple simultaneous gate conditions need exact semantics

## F25. Failure escalation and parent decision logic

- Status: `identified`
- Priority: `critical`
- Description: Child failures should escalate only to parents, with parent-side decisions driving retry, replan, or deferment.
- Related specs:
  - `notes/node_lifecycle_spec_revised.md`
- Expected artifacts:
  - failure summary model
  - threshold rules
  - parent decision pseudocode
- Known gaps:
  - full decision tree is not yet written

## F26. Hook system

- Status: `identified`
- Priority: `high`
- Description: Hooks should inject project- or policy-driven behavior at lifecycle points.
- Related specs:
  - `notes/yaml_schemas_spec_revised.md`
- Expected artifacts:
  - hook schema
  - insertion algorithm
  - hook ordering rules
- Known gaps:
  - interactions between multiple hooks at the same point need stricter rules

## F27. Source document lineage

- Status: `identified`
- Priority: `high`
- Description: Every compiled workflow should preserve exact source YAML and override lineage.
- Related specs:
  - `notes/yaml_schemas_spec_revised.md`
  - `notes/database_schema_spec_revised.md`
- Expected artifacts:
  - source lineage tables
  - compile-time lineage capture
  - CLI inspection
- Known gaps:
  - source role taxonomy should be frozen

## F28. Prompt history and summary history

- Status: `identified`
- Priority: `medium`
- Description: Prompt and summary history should be persisted and queryable for auditability.
- Related specs:
  - `notes/database_schema_spec_revised.md`
  - `notes/cli_surface_spec_revised.md`
- Expected artifacts:
  - prompt and summary persistence
  - query CLI
  - linkages to subtasks and runs
- Known gaps:
  - summary type taxonomy still needs tightening

## F29. Documentation generation

- Status: `specified`
- Priority: `medium`
- Description: The system should build documentation from code, provenance, and node history.
- Related specs:
  - `notes/original_concept.md`
  - `notes/cli_surface_spec_revised.md`
- Expected artifacts:
  - docs build tasks
  - docs storage model
  - merged/local view rules
- Known gaps:
  - doc source blending rules need explicit pseudocode

## F30. Code provenance and rationale mapping

- Status: `resolved_in_principle`
- Priority: `high`
- Description: Code entities and their rationale should be linked back to nodes, prompts, and changes.
- Related specs:
  - `notes/database_schema_spec_revised.md`
  - `notes/original_concept.md`
- Expected artifacts:
  - entity extraction logic
  - relation tracking
  - rationale surfaces
- Known gaps:
  - stable entity identity across refactors needs more design

## F31. Daemon authority and durable orchestration record

- Status: `specified`
- Priority: `critical`
- Description: The daemon should own live orchestration while the database remains the durable canonical record for recovery, auditability, and operator inspection.
- Related specs:
  - `notes/authority_and_api_model.md`
  - `notes/database_schema_spec_v2.md`
  - `notes/runtime_command_loop_spec_v2.md`
  - `notes/cli_surface_spec_v2.md`
- Expected artifacts:
  - daemon/API authority model
  - persistence rules
  - no-hidden-state review checklist
  - CLI/API read paths
- Known gaps:
  - some older planning docs still use the superseded "DB truth source" shorthand
  - implementation-time daemon locking and auth details still need to be built

## F32. Automation of all user-visible actions

- Status: `resolved_in_principle`
- Priority: `high`
- Description: Every user-visible action should have a CLI/runtime path and audit trail.
- Related specs:
  - `notes/original_concept.md`
  - `notes/cli_surface_spec_revised.md`
- Expected artifacts:
  - action matrix
  - command mapping
  - mutation audit rules
- Known gaps:
  - the full action matrix has not yet been written

## F33. Optional isolated runtime environments

- Status: `identified`
- Priority: `medium`
- Description: Some child work may require isolated containers or namespace environments.
- Related specs:
  - `notes/original_concept.md`
- Expected artifacts:
  - environment policy schema
  - launch strategy
  - environment metadata persistence
- Known gaps:
  - this area remains mostly conceptual and needs dedicated design treatment

## F34. Provider-agnostic session recovery

- Status: `identified`
- Priority: `medium`
- Description: Resume should work even when provider session IDs are inconsistent or unavailable.
- Related specs:
  - `notes/original_concept.md`
  - `notes/runtime_command_loop_spec.md`
- Expected artifacts:
  - resume fallbacks
  - session rebinding logic
  - provider capability matrix
- Known gaps:
  - capability assumptions need to be made explicit

## F35. Project policy extensibility

- Status: `identified`
- Priority: `high`
- Description: Projects should be able to redefine ladders, hooks, policies, and quality gates.
- Related specs:
  - `notes/original_concept.md`
  - `notes/yaml_schemas_spec_revised.md`
- Expected artifacts:
  - extensibility schema
  - override examples
  - project policy docs
- Known gaps:
  - scope boundaries between system-level and project-level policy need sharper rules

## F36. Auditable history and reproducibility

- Status: `identified`
- Priority: `critical`
- Description: The system should be reconstructible and auditable from stored YAML, DB, git, prompts, and summaries.
- Related specs:
  - all major revised specs
- Expected artifacts:
  - audit trail queries
  - reproducibility checklist
  - no-hidden-state validation
- Known gaps:
  - a dedicated auditability checklist should likely be written

---

## Suggested Next Tracking Documents

To make this feature inventory operational, create the following follow-on artifacts:

- `notes/spec_traceability_matrix.md`
- `notes/cross_spec_gap_matrix.md`
- `notes/yaml_inventory_v2.md`
- `notes/runtime_pseudocode_plan.md`

Those documents should reference feature IDs from this inventory directly.

---

## Maintenance Rule

Whenever a new major design requirement appears, either:

1. attach it to an existing feature in this document, or
2. add a new feature ID here before updating downstream specs

This keeps the design review process anchored to tracked capabilities rather than drifting into isolated document edits.
