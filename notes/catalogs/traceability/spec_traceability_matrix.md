# Spec Traceability Matrix

## Purpose

This document maps original design goals and major tracked features to the current specification artifacts.

It exists to answer:

- which design goals are already represented
- which major features are now covered by the v2 spec package
- which concrete artifacts still need implementation-facing follow-through
- which gaps remain true design gaps versus implementation-open items

This document should be reviewed and updated during every major spec revision pass.

Related documents:

- `notes/explorations/original_concept.md`
- `notes/planning/expansion/full_spec_expansion_plan.md`
- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/checklists/feature_checklist_standard.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`

---

## Status Model

Use the following coverage values:

- `covered`
- `partially_covered`
- `missing`
- `contradictory`
- `implementation_open`

Use the following artifact-state values when useful:

- `exists`
- `exists_but_needs_fold_in`
- `missing`

Interpretation rule:

- `covered` and `partially_covered` in this document describe specification and artifact coverage only.
- They do not mean a feature is `verified`, `flow_complete`, or `release_ready`.
- Canonical implementation and verification status lives in:
  - `notes/catalogs/checklists/feature_checklist_standard.md`
  - `notes/catalogs/checklists/feature_checklist_backfill.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`

---

## Original Design Goal Inventory

The following goal IDs are normalized from `notes/explorations/original_concept.md`.

| Goal ID | Design Goal |
| --- | --- |
| G01 | Define work declaratively in YAML. |
| G02 | Enforce prerequisites, checks, and bounce-back behavior when requirements are not met. |
| G03 | Model work as nodes with tasks and subtasks rather than loosely structured prompts. |
| G04 | Support configurable hierarchy levels instead of hardcoding one ladder. |
| G05 | Allow epics/phases/plans/tasks or custom layers to plan and execute recursively. |
| G06 | Support child/sibling dependency graphs with valid dependency restrictions. |
| G07 | Allow both automatic decomposition and manual tree construction. |
| G08 | Persist full lineage of prompts, plans, summaries, changes, and rationale. |
| G09 | Use git branches per node and merge children back to parents deterministically. |
| G10 | Support subtree regeneration and upstream rebuild when a node changes. |
| G11 | Persist a database of code relations, rationale, and changes. |
| G12 | Allow deterministic reconstruction from prompts/specs where possible. |
| G13 | Support optional isolated child environments for special workloads. |
| G14 | Ensure everything the user can do is automatable. |
| G15 | Provide a CLI for AIs and operators to inspect runtime, rationale, and history. |
| G16 | Support project-defined hooks, testing, and quality gates. |
| G17 | Run AI sessions in tmux and track session identity and recovery data. |
| G18 | Support resume/recovery if tmux or host state is lost. |
| G19 | Nudge or recover idle/stuck sessions without losing the current stage. |
| G20 | Generate documentation using static analysis plus relational/rationale data. |

---

## Goal To Feature Mapping

This table maps the original goals to tracked feature IDs from `notes/catalogs/inventory/major_feature_inventory.md`.

| Goal ID | Feature IDs |
| --- | --- |
| G01 | F04, F05, F06 |
| G02 | F21, F24, F25 |
| G03 | F01, F03, F07, F09 |
| G04 | F01, F35 |
| G05 | F01, F15, F19, F35 |
| G06 | F08 |
| G07 | F15, F16 |
| G08 | F27, F28, F30, F36 |
| G09 | F17, F18, F36 |
| G10 | F02, F19, F20 |
| G11 | F30, F31 |
| G12 | F02, F03, F36 |
| G13 | F33 |
| G14 | F10, F11, F32 |
| G15 | F10, F11, F28, F30 |
| G16 | F21, F22, F23, F26, F35 |
| G17 | F12 |
| G18 | F12, F34 |
| G19 | F13 |
| G20 | F29, F30 |

---

## Feature Traceability Matrix

This matrix maps each feature to the current spec package and the remaining level of specification closure.

| Feature ID | Feature | Current Specs | YAML | DB | CLI | Pseudocode | Prompts | Coverage | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F01 | Configurable node hierarchy | `yaml_schemas_spec_v2`, `node_lifecycle_spec_v2`, `major_feature_inventory` | exists | exists | exists_but_needs_fold_in | exists |  | covered | Generic tiers/kinds and parent/child constraints are now part of the canonical model. |
| F02 | Node versioning and supersession | `database_schema_spec_v2`, `node_lifecycle_spec_v2`, `git_rectification_spec_v2`, `cutover_policy_note` | exists_but_needs_fold_in | exists | exists_but_needs_fold_in | exists |  | covered | Durable node version history, supersession, candidate cutover, and current-version selection are implemented; remaining caveats are about later live git/cutover refinement rather than missing core feature behavior. |
| F03 | Immutable workflow compilation | `yaml_schemas_spec_v2`, `database_schema_spec_v2`, `runtime_command_loop_spec_v2`, `compile_failure_persistence`, `override_conflict_semantics`, `hook_expansion_algorithm` | exists | exists | exists_but_needs_fold_in | exists |  | covered | Compile persistence, compile-failure diagnostics, stage inspection surfaces, hook expansion, and frozen rendering payloads are all implemented. |
| F04 | YAML schema system | `yaml_schemas_spec_v2`, `yaml_inventory_v2` | exists | exists_but_needs_fold_in | exists_but_needs_fold_in | exists |  | covered | The family inventory and canonical schemas now exist at spec level. |
| F05 | Default YAML library | `default_yaml_library_plan`, `prompt_library_plan`, `yaml_schemas_spec_v2` | exists | exists_but_needs_fold_in | exists_but_needs_fold_in | exists_but_needs_fold_in | x | covered | The built-in node/task/layout/quality/runtime library and prompt pack are authored, validated, and inspected by dedicated integrity checks. |
| F06 | Override and merge resolution | `yaml_schemas_spec_v2`, `override_conflict_semantics`, `database_schema_spec_v2` | exists | exists | exists_but_needs_fold_in | exists |  | covered | Deterministic override folding, warnings, conflicts, and workflow-stage inspection are implemented. |
| F07 | Durable node lifecycle state | `node_lifecycle_spec_v2`, `database_schema_spec_v2`, `state_value_catalog` | exists_but_needs_fold_in | exists | exists | exists |  | covered | Lifecycle and run-state concepts are now strong and bounded. |
| F08 | Dependency graph and admission control | `node_lifecycle_spec_v2`, `database_schema_spec_v2`, `invalid_dependency_graph_handling`, `child_materialization_and_scheduling`, `cli_surface_spec_v2` | exists_but_needs_fold_in | exists | exists | exists |  | covered | Dependency storage, readiness checks, blocker persistence, invalid-graph rejection, and operator inspection are implemented. |
| F09 | Node run orchestration | `node_lifecycle_spec_v2`, `runtime_command_loop_spec_v2`, `database_schema_spec_v2`, `prompt_library_plan` | exists | exists | exists | exists | x | covered | The canonical node-loop and cursor model are now explicit, and default operational prompt payloads are now drafted. |
| F10 | AI-facing CLI command loop | `runtime_command_loop_spec_v2`, `cli_surface_spec_v2`, `prompt_library_plan` | exists_but_needs_fold_in | exists_but_needs_fold_in | exists | exists | x | covered | AI-facing commands and ownership model are now explicit, and the bootstrap/missed-step CLI guidance prompts are drafted. |
| F11 | Operator CLI and introspection | `cli_surface_spec_v2`, `action_automation_matrix`, `database_schema_spec_v2` | exists_but_needs_fold_in | exists | exists | exists_but_needs_fold_in |  | covered | Operator structure, state, history, artifact, and audit reads are implemented across CLI, daemon, and DB-backed views. |
| F12 | Session binding and resume | `runtime_command_loop_spec_v2`, `tmux_session_lifecycle_spec_v1`, `database_schema_spec_v2`, `cli_surface_spec_v2` | exists_but_needs_fold_in | exists | exists | exists |  | covered | Durable session binding, current-session inspection, attach/resume flows, and recovery classification are implemented. |
| F13 | Idle detection and nudge behavior | `runtime_command_loop_spec_v2`, `node_lifecycle_spec_v2`, `state_value_catalog`, `prompt_library_plan` | exists_but_needs_fold_in | exists_but_needs_fold_in | exists | exists | x | covered | Idle polling, screen classification, bounded nudge escalation, and pause-on-exhaustion behavior are implemented. |
| F14 | Optional pushed child sessions | `runtime_command_loop_spec_v2`, `child_session_mergeback_contract`, `database_schema_spec_v2`, `cli_surface_spec_v2`, `prompt_library_plan` | exists_but_needs_fold_in | exists_but_needs_fold_in | exists | exists | x | covered | Child-session push/pop and durable merge-back result persistence are implemented. |
| F15 | Child node spawning | `yaml_schemas_spec_v2`, `child_materialization_and_scheduling`, `node_lifecycle_spec_v2`, `runtime_command_loop_spec_v2`, `prompt_library_plan` | exists | exists_but_needs_fold_in | exists_but_needs_fold_in | exists | x | covered | Durable child materialization, readiness classification, and child-materialization inspection are implemented. |
| F16 | Manual tree construction | `node_lifecycle_spec_v2`, `manual_vs_auto_tree_interaction`, `child_materialization_and_scheduling` | exists_but_needs_fold_in | exists_but_needs_fold_in | exists_but_needs_fold_in | exists |  | covered | Manual child creation now participates in the same durable authority model as layout-owned trees. |
| F17 | Deterministic branch model | `git_rectification_spec_v2`, `cutover_policy_note`, `database_schema_spec_v2` | exists_but_needs_fold_in | exists | exists_but_needs_fold_in | exists |  | covered | Canonical branch naming, seed/final commit anchors, and branch inspection are implemented. |
| F18 | Child merge and reconcile pipeline | `git_rectification_spec_v2`, `node_lifecycle_spec_v2`, `runtime_command_loop_spec_v2`, `prompt_library_plan` | exists | exists | exists | exists | x | covered | Merge/reconcile flow and parent-local reconcile prompts are explicit, and the next implementation direction now includes daemon-owned incremental child-to-parent merge for sibling visibility before final parent reconcile. |
| F19 | Regeneration and upstream rectification | `git_rectification_spec_v2`, `node_lifecycle_spec_v2`, `cutover_policy_note`, `prompt_library_plan` | exists | exists | exists_but_needs_fold_in | exists | x | covered | Regeneration and upstream rectification are implemented as durable rebuild lineages; only live git execution remains intentionally deferred. |
| F20 | Conflict detection and resolution | `git_rectification_spec_v2`, `database_schema_spec_v2` | exists | exists | exists | exists |  | covered | Conflict persistence and resolution flow are now explicit enough at spec level. |
| F21 | Validation framework | `yaml_schemas_spec_v2`, `database_schema_spec_v2`, `node_lifecycle_spec_v2`, `cli_surface_spec_v2`, `prompt_library_plan` | exists | exists | exists | exists | x | covered | Validation is now a first-class stage with result persistence, and the missed-step/validation-failure prompts are drafted. |
| F22 | Review framework | `yaml_schemas_spec_v2`, `review_testing_docs_yaml_plan`, `database_schema_spec_v2`, `cli_surface_spec_v2`, `prompt_library_plan` | exists | exists | exists | exists | x | covered | Review is now first-class across YAML, DB, runtime, and CLI, with default review prompt templates drafted. |
| F23 | Testing framework integration | `yaml_schemas_spec_v2`, `review_testing_docs_yaml_plan`, `database_schema_spec_v2`, `cli_surface_spec_v2`, `prompt_library_plan` | exists | exists | exists | exists | x | covered | Testing is now first-class across the spec package, with default testing-stage prompt guidance drafted. |
| F24 | User gating and pause flags | `node_lifecycle_spec_v2`, `runtime_command_loop_spec_v2`, `pause_workflow_event_persistence`, `cli_surface_spec_v2`, `prompt_library_plan` | exists | exists | exists | exists | x | covered | Pause gates, approval-before-resume, durable pause-state introspection, and bounded pause workflow events are now implemented and folded into the current note set. |
| F25 | Failure escalation and parent decision logic | `parent_failure_decision_spec`, `node_lifecycle_spec_v2`, `runtime_command_loop_spec_v2`, `prompt_library_plan` | exists_but_needs_fold_in | exists_but_needs_fold_in | exists_but_needs_fold_in | exists | x | covered | Durable child-failure counters, parent decision history, and response commands are implemented. |
| F26 | Hook system | `yaml_schemas_spec_v2`, `hook_expansion_algorithm`, `runtime_command_loop_spec_v2` | exists | exists_but_needs_fold_in | exists | exists |  | covered | Compile-time hook selection, ordering, expansion, and hook-inspection surfaces are implemented. |
| F27 | Source document lineage | `yaml_schemas_spec_v2`, `database_schema_spec_v2`, `cli_surface_spec_v2`, `state_value_catalog` | exists | exists | exists | exists_but_needs_fold_in |  | covered | Durable source-document lineage and workflow/node source inspection are implemented. |
| F28 | Prompt history and summary history | `database_schema_spec_v2`, `cli_surface_spec_v2`, `runtime_command_loop_spec_v2`, `state_value_catalog`, `prompt_library_plan` | exists_but_needs_fold_in | exists | exists | exists | x | covered | Prompt delivery and summary registration now have durable history plus CLI/daemon inspection surfaces. |
| F29 | Documentation generation | `yaml_schemas_spec_v2`, `review_testing_docs_yaml_plan`, `database_schema_spec_v2`, `cli_surface_spec_v2`, `prompt_library_plan` | exists | exists | exists | exists | x | covered | Docs are now first-class and ordered correctly relative to provenance/finalize, with default docs prompts drafted. |
| F30 | Code provenance and rationale mapping | `database_schema_spec_v2`, `provenance_identity_strategy`, `cli_surface_spec_v2`, `auditability_checklist` | exists_but_needs_fold_in | exists | exists | exists |  | covered | Code-entity extraction, node/entity change history, rationale reads, and relation history are implemented with a bounded multilanguage extractor spanning Python plus JS/TS implementation code. |
| F31 | Daemon authority and durable orchestration record | `authority_and_api_model`, `database_schema_spec_v2`, `runtime_command_loop_spec_v2`, `cli_surface_spec_v2`, `auditability_checklist` | exists | exists | exists | exists |  | covered | The live-authority and durable-record boundary is now explicit across the package. |
| F32 | Automation of all user-visible actions | `action_automation_matrix`, `cli_surface_spec_v2`, `implementation_slicing_plan` | exists_but_needs_fold_in | exists_but_needs_fold_in | exists | exists |  | covered | User-visible runtime mutations now have daemon-backed CLI surfaces and durable audit for the implemented command families. |
| F33 | Optional isolated runtime environments | `runtime_environment_policy_note`, `yaml_schemas_spec_v2`, `implementation_slicing_plan` | exists_but_needs_fold_in | exists_but_needs_fold_in | exists_but_needs_fold_in | exists |  | covered | Environment-policy selection and frozen runtime environment metadata are implemented; real launcher isolation remains intentionally deferred. |
| F34 | Provider-agnostic session recovery | `tmux_session_lifecycle_spec_v1`, `runtime_command_loop_spec_v2`, `database_schema_spec_v2`, `prompt_library_plan` | exists_but_needs_fold_in | exists | exists | exists | x | covered | Provider-agnostic recovery classification, recommended actions, and resume/replacement flows are implemented. |
| F35 | Project policy extensibility | `yaml_schemas_spec_v2`, `override_conflict_semantics`, `runtime_environment_policy_note`, `prompt_library_plan` | exists | exists_but_needs_fold_in | exists_but_needs_fold_in | exists | x | covered | Effective project policy resolution, policy impact, prompt-pack selection, and workflow policy inspection are implemented. |
| F36 | Auditable history and reproducibility | `auditability_checklist`, all v2 specs, `cross_spec_gap_matrix`, `prompt_library_plan` | exists | exists | exists | exists | x | covered | Auditability is now a first-class review dimension rather than only a design slogan, and the default prompt pack is explicit enough to be reviewed. |

---

## Artifact Type Inventory

This section lists the concrete artifact families the system should eventually have. Use this as a checklist when filling in missing traceability.

### Current core specs

| Artifact | State |
| --- | --- |
| `notes/explorations/original_concept.md` | exists |
| `notes/archive/superseded/yaml_schemas_spec_revised.md` | exists |
| `notes/archive/superseded/database_schema_spec_revised.md` | exists |
| `notes/archive/superseded/node_lifecycle_spec_revised.md` | exists |
| `notes/archive/superseded/runtime_command_loop_spec.md` | exists |
| `notes/archive/superseded/cli_surface_spec_revised.md` | exists |
| `notes/archive/superseded/git_rectification_spec_revised.md` | exists |
| `notes/planning/expansion/full_spec_expansion_plan.md` | exists |
| `notes/catalogs/inventory/major_feature_inventory.md` | exists |

### Supporting planning and review artifacts

| Artifact | State | Purpose |
| --- | --- | --- |
| `notes/catalogs/inventory/yaml_inventory_v2.md` | exists | Full YAML schema family and file inventory. |
| `notes/catalogs/inventory/default_yaml_library_plan.md` | exists | Concrete default YAML file set and relationships. |
| `notes/planning/expansion/database_schema_v2_expansion.md` | exists | Migration-grade DB detail and constraints. |
| `notes/planning/expansion/runtime_pseudocode_plan.md` | exists | End-to-end pseudocode modules and flow ownership. |
| `notes/catalogs/traceability/cross_spec_gap_matrix.md` | exists | Consolidated gap and contradiction review. |
| `notes/catalogs/audit/auditability_checklist.md` | exists | Reproducibility and no-hidden-state review checklist. |
| `notes/catalogs/traceability/action_automation_matrix.md` | exists | Mapping of user-visible actions to CLI/runtime/DB changes. |
| `notes/specs/prompts/prompt_library_plan.md` | exists | Default prompt pack for generation, runtime guidance, recovery, and failure handling. |

### Canonical v2 specs

| Artifact | State | Purpose |
| --- | --- | --- |
| `notes/specs/yaml/yaml_schemas_spec_v2.md` | exists | Canonical v2 YAML schema spec. |
| `notes/specs/database/database_schema_spec_v2.md` | exists | Canonical v2 DB spec. |
| `notes/specs/runtime/node_lifecycle_spec_v2.md` | exists | Canonical v2 lifecycle spec. |
| `notes/specs/runtime/runtime_command_loop_spec_v2.md` | exists | Canonical v2 runtime loop spec. |
| `notes/specs/cli/cli_surface_spec_v2.md` | exists | Canonical v2 CLI spec. |
| `notes/specs/git/git_rectification_spec_v2.md` | exists | Canonical v2 git/rectification spec. |

### Focused appendix and closure notes

| Artifact | State | Purpose |
| --- | --- | --- |
| `notes/contracts/parent_child/parent_failure_decision_spec.md` | exists | Failure-classification and parent decision logic. |
| `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md` | exists | Primary tmux session lifecycle, recovery classification, prompt bootstrap, and replacement/resume model. |
| `notes/contracts/yaml/override_conflict_semantics.md` | exists | Deterministic override merge and conflict rules. |
| `notes/contracts/runtime/cutover_policy_note.md` | exists | Candidate versus authoritative lineage and cutover timing. |
| `notes/specs/provenance/provenance_identity_strategy.md` | exists | Code-entity identity strategy over time. |
| `notes/contracts/persistence/compile_failure_persistence.md` | exists | Compile-failure stages, classes, and persistence model. |
| `notes/contracts/runtime/runtime_environment_policy_note.md` | exists | Optional isolated execution policy. |
| `notes/catalogs/vocabulary/state_value_catalog.md` | exists | Shared bounded vocabulary for statuses and types. |
| `notes/contracts/parent_child/child_materialization_and_scheduling.md` | exists | Child creation and readiness model. |
| `notes/contracts/yaml/hook_expansion_algorithm.md` | exists | Hook selection, ordering, and expansion algorithm. |
| `notes/contracts/runtime/invalid_dependency_graph_handling.md` | exists | Structural and runtime dependency validation rules. |
| `notes/contracts/parent_child/manual_vs_auto_tree_interaction.md` | exists | Manual/layout authority and hybrid-tree behavior. |
| `notes/contracts/parent_child/child_session_mergeback_contract.md` | exists | Parent/child-session return payload contract. |
| `notes/contracts/persistence/pause_workflow_event_persistence.md` | exists | Narrow workflow-event persistence model. |
| `notes/planning/implementation/implementation_slicing_plan.md` | exists | Dependency-ordered implementation slices. |

---

## Current Remaining Gaps

Based on the current traceability pass, the biggest remaining gaps are:

1. Live git execution remains intentionally deferred. The durable lineage, merge, and rectification model exists, but safe `git reset`/`merge`/finalize working-tree execution is still staged.
2. Planning/config mutation surfaces are still incomplete. Layout update/generation and project-policy update flows are not yet formalized as daemon-backed operator commands.
3. Provenance remains intentionally bounded. The extractor is Python-first and identity across large refactors is still confidence-based rather than perfectly deterministic.
4. Optional isolated runtime environments stop at policy and metadata today. Real launcher implementations, cleanup semantics, and resource accounting remain deferred.
5. Some appendix and implementation decisions still need further fold-in to the core v2 specs so the traceability status can eventually move from “exists_but_needs_fold_in” to fully canonical.

---

## Review Procedure

During each review cycle:

1. update feature statuses in `notes/catalogs/inventory/major_feature_inventory.md`
2. update coverage values in this matrix
3. add any newly discovered artifacts to the artifact inventory
4. record new gaps in `notes/catalogs/traceability/cross_spec_gap_matrix.md`
5. feed missing items into v2 rewrites or follow-on planning docs

---

## Maintenance Rule

If a new major requirement is discovered:

1. add or update the feature in `notes/catalogs/inventory/major_feature_inventory.md`
2. add or update the goal mapping in this document if needed
3. record the missing artifact family here
4. reflect the gap in the dedicated gap matrix

This keeps feature tracking, traceability, and gap review synchronized.
