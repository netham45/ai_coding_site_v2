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

This matrix maps each feature to the current spec package and the remaining level of closure.

| Feature ID | Feature | Current Specs | YAML | DB | CLI | Pseudocode | Prompts | Coverage | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F01 | Configurable node hierarchy | `yaml_schemas_spec_v2`, `node_lifecycle_spec_v2`, `major_feature_inventory` | exists | exists | exists_but_needs_fold_in | exists |  | covered | Generic tiers/kinds and parent/child constraints are now part of the canonical model. |
| F02 | Node versioning and supersession | `database_schema_spec_v2`, `node_lifecycle_spec_v2`, `git_rectification_spec_v2`, `cutover_policy_note` | exists_but_needs_fold_in | exists | exists_but_needs_fold_in | exists |  | implementation_open | Core lineage model is strong; active-old-run handling and authority modeling still need final implementation choices. |
| F03 | Immutable workflow compilation | `yaml_schemas_spec_v2`, `database_schema_spec_v2`, `runtime_command_loop_spec_v2`, `compile_failure_persistence`, `override_conflict_semantics`, `hook_expansion_algorithm` | exists | exists | exists_but_needs_fold_in | exists |  | implementation_open | Compile boundary is now well defined, but implementation-grade folding of compile failures and hook expansion is still needed. |
| F04 | YAML schema system | `yaml_schemas_spec_v2`, `yaml_inventory_v2` | exists | exists_but_needs_fold_in | exists_but_needs_fold_in | exists |  | covered | The family inventory and canonical schemas now exist at spec level. |
| F05 | Default YAML library | `default_yaml_library_plan`, `prompt_library_plan`, `yaml_schemas_spec_v2` | missing | exists_but_needs_fold_in | exists_but_needs_fold_in | exists_but_needs_fold_in | x | implementation_open | The library is planned clearly, and the prompt pack is now drafted, but the actual built-in YAML files are still not authored. |
| F06 | Override and merge resolution | `yaml_schemas_spec_v2`, `override_conflict_semantics`, `database_schema_spec_v2` | exists | exists | exists_but_needs_fold_in | exists |  | implementation_open | Merge modes and conflict classes are defined; exact compile implementation still needs to be built. |
| F07 | Durable node lifecycle state | `node_lifecycle_spec_v2`, `database_schema_spec_v2`, `state_value_catalog` | exists_but_needs_fold_in | exists | exists | exists |  | covered | Lifecycle and run-state concepts are now strong and bounded. |
| F08 | Dependency graph and admission control | `node_lifecycle_spec_v2`, `database_schema_spec_v2`, `invalid_dependency_graph_handling`, `child_materialization_and_scheduling`, `cli_surface_spec_v2` | exists_but_needs_fold_in | exists | exists | exists |  | implementation_open | Major design gaps are much smaller, but dependency validation and scheduling need implementation-grade refinement. |
| F09 | Node run orchestration | `node_lifecycle_spec_v2`, `runtime_command_loop_spec_v2`, `database_schema_spec_v2`, `prompt_library_plan` | exists | exists | exists | exists | x | covered | The canonical node-loop and cursor model are now explicit, and default operational prompt payloads are now drafted. |
| F10 | AI-facing CLI command loop | `runtime_command_loop_spec_v2`, `cli_surface_spec_v2`, `prompt_library_plan` | exists_but_needs_fold_in | exists_but_needs_fold_in | exists | exists | x | covered | AI-facing commands and ownership model are now explicit, and the bootstrap/missed-step CLI guidance prompts are drafted. |
| F11 | Operator CLI and introspection | `cli_surface_spec_v2`, `action_automation_matrix`, `database_schema_spec_v2` | exists_but_needs_fold_in | exists | exists | exists_but_needs_fold_in |  | implementation_open | Broad operator visibility is specified, but mutation guardrails still need final policy. |
| F12 | Session binding and resume | `runtime_command_loop_spec_v2`, `database_schema_spec_v2`, `cli_surface_spec_v2`, `session_recovery_appendix` | exists_but_needs_fold_in | exists | exists | exists |  | resolved_in_principle | Recovery and resume are now well designed, pending canonical fold-in and implementation detail. |
| F13 | Idle detection and nudge behavior | `runtime_command_loop_spec_v2`, `node_lifecycle_spec_v2`, `state_value_catalog`, `prompt_library_plan` | exists_but_needs_fold_in | exists_but_needs_fold_in | exists | exists | x | implementation_open | Semantics are mostly defined, and the default idle-nudge prompt now exists, but policy defaults and escalation thresholds remain. |
| F14 | Optional pushed child sessions | `runtime_command_loop_spec_v2`, `child_session_mergeback_contract`, `database_schema_spec_v2`, `cli_surface_spec_v2`, `prompt_library_plan` | exists_but_needs_fold_in | exists_but_needs_fold_in | exists | exists | x | implementation_open | The merge-back contract is now explicit, and the delegated research prompt is drafted, but dedicated result persistence may still be needed. |
| F15 | Child node spawning | `yaml_schemas_spec_v2`, `child_materialization_and_scheduling`, `node_lifecycle_spec_v2`, `runtime_command_loop_spec_v2`, `prompt_library_plan` | exists | exists_but_needs_fold_in | exists_but_needs_fold_in | exists | x | implementation_open | Materialization and scheduling now have a dedicated design, and phase/plan/task layout prompts are drafted, but canonical fold-in remains. |
| F16 | Manual tree construction | `node_lifecycle_spec_v2`, `manual_vs_auto_tree_interaction`, `child_materialization_and_scheduling` | exists_but_needs_fold_in | exists_but_needs_fold_in | exists_but_needs_fold_in | exists |  | implementation_open | Manual-vs-auto coexistence is now defined, but likely needs explicit authority metadata in implementation. |
| F17 | Deterministic branch model | `git_rectification_spec_v2`, `cutover_policy_note`, `database_schema_spec_v2` | exists_but_needs_fold_in | exists | exists_but_needs_fold_in | exists |  | implementation_open | Branch semantics are strong, but exact naming pattern still needs freezing. |
| F18 | Child merge and reconcile pipeline | `git_rectification_spec_v2`, `node_lifecycle_spec_v2`, `runtime_command_loop_spec_v2`, `prompt_library_plan` | exists | exists | exists | exists | x | covered | Deterministic merge order and reconcile flow are now explicit, and the parent-local reconcile prompt is drafted. |
| F19 | Regeneration and upstream rectification | `git_rectification_spec_v2`, `node_lifecycle_spec_v2`, `cutover_policy_note`, `prompt_library_plan` | exists | exists | exists_but_needs_fold_in | exists | x | implementation_open | Rebuild model is strong; prompt guidance for regenerated execution/reconcile is now drafted, but active-old-run and authority cutover details still remain. |
| F20 | Conflict detection and resolution | `git_rectification_spec_v2`, `database_schema_spec_v2` | exists | exists | exists | exists |  | covered | Conflict persistence and resolution flow are now explicit enough at spec level. |
| F21 | Validation framework | `yaml_schemas_spec_v2`, `database_schema_spec_v2`, `node_lifecycle_spec_v2`, `cli_surface_spec_v2`, `prompt_library_plan` | exists | exists | exists | exists | x | covered | Validation is now a first-class stage with result persistence, and the missed-step/validation-failure prompts are drafted. |
| F22 | Review framework | `yaml_schemas_spec_v2`, `review_testing_docs_yaml_plan`, `database_schema_spec_v2`, `cli_surface_spec_v2`, `prompt_library_plan` | exists | exists | exists | exists | x | covered | Review is now first-class across YAML, DB, runtime, and CLI, with default review prompt templates drafted. |
| F23 | Testing framework integration | `yaml_schemas_spec_v2`, `review_testing_docs_yaml_plan`, `database_schema_spec_v2`, `cli_surface_spec_v2`, `prompt_library_plan` | exists | exists | exists | exists | x | covered | Testing is now first-class across the spec package, with default testing-stage prompt guidance drafted. |
| F24 | User gating and pause flags | `node_lifecycle_spec_v2`, `runtime_command_loop_spec_v2`, `pause_workflow_event_persistence`, `cli_surface_spec_v2`, `prompt_library_plan` | exists | exists_but_needs_fold_in | exists | exists | x | implementation_open | Pause semantics are strong, and the pause/approval prompt payloads are now drafted, but workflow-event persistence is still an implementation-facing choice. |
| F25 | Failure escalation and parent decision logic | `parent_failure_decision_spec`, `node_lifecycle_spec_v2`, `runtime_command_loop_spec_v2`, `prompt_library_plan` | exists_but_needs_fold_in | exists_but_needs_fold_in | exists_but_needs_fold_in | exists | x | resolved_in_principle | Dedicated failure-decision logic now exists, and parent pause/replan prompt templates are drafted, pending full canonical fold-in. |
| F26 | Hook system | `yaml_schemas_spec_v2`, `hook_expansion_algorithm`, `runtime_command_loop_spec_v2` | exists | exists_but_needs_fold_in | exists | exists |  | implementation_open | Hook design is now much stronger, but expansion diagnostics and final fold-in remain. |
| F27 | Source document lineage | `yaml_schemas_spec_v2`, `database_schema_spec_v2`, `cli_surface_spec_v2`, `state_value_catalog` | exists | exists | exists | exists_but_needs_fold_in |  | implementation_open | Strong lineage model exists; source-role taxonomy still needs final normalization in implementation artifacts. |
| F28 | Prompt history and summary history | `database_schema_spec_v2`, `cli_surface_spec_v2`, `runtime_command_loop_spec_v2`, `state_value_catalog`, `prompt_library_plan` | exists_but_needs_fold_in | exists | exists | exists | x | implementation_open | Prompt history is strong, and the default prompt pack is now defined at note level; summary taxonomy still needs final implementation normalization. |
| F29 | Documentation generation | `yaml_schemas_spec_v2`, `review_testing_docs_yaml_plan`, `database_schema_spec_v2`, `cli_surface_spec_v2`, `prompt_library_plan` | exists | exists | exists | exists | x | covered | Docs are now first-class and ordered correctly relative to provenance/finalize, with default docs prompts drafted. |
| F30 | Code provenance and rationale mapping | `database_schema_spec_v2`, `provenance_identity_strategy`, `cli_surface_spec_v2`, `auditability_checklist` | exists_but_needs_fold_in | exists | exists | exists |  | resolved_in_principle | The provenance identity problem is now addressed conceptually, pending implementation-grade folding. |
| F31 | Daemon authority and durable orchestration record | `authority_and_api_model`, `database_schema_spec_v2`, `runtime_command_loop_spec_v2`, `cli_surface_spec_v2`, `auditability_checklist` | exists | exists | exists | exists |  | covered | The live-authority and durable-record boundary is now explicit across the package. |
| F32 | Automation of all user-visible actions | `action_automation_matrix`, `cli_surface_spec_v2`, `implementation_slicing_plan` | exists_but_needs_fold_in | exists_but_needs_fold_in | exists | exists |  | resolved_in_principle | The mapping now exists; remaining work is implementation and command-guardrail detail. |
| F33 | Optional isolated runtime environments | `runtime_environment_policy_note`, `yaml_schemas_spec_v2`, `implementation_slicing_plan` | exists_but_needs_fold_in | exists_but_needs_fold_in | exists_but_needs_fold_in | exists |  | implementation_open | The capability is now defined as bounded optional/deferred, not missing. |
| F34 | Provider-agnostic session recovery | `session_recovery_appendix`, `runtime_command_loop_spec_v2`, `database_schema_spec_v2`, `prompt_library_plan` | exists_but_needs_fold_in | exists | exists | exists | x | resolved_in_principle | Recovery priorities and fallback rules are now explicit, and resume/replacement prompt templates are drafted. |
| F35 | Project policy extensibility | `yaml_schemas_spec_v2`, `override_conflict_semantics`, `runtime_environment_policy_note`, `prompt_library_plan` | exists | exists_but_needs_fold_in | exists_but_needs_fold_in | exists | x | implementation_open | Extensibility is now much clearer, and prompt packs are now treated as overrideable project assets, though policy/runtime compile boundaries still need care. |
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
| `notes/contracts/runtime/session_recovery_appendix.md` | exists | Recovery scenarios and replacement-session model. |
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

Based on the current traceability pass and the normalized gap matrix, the biggest remaining gaps are:

1. The concrete default built-in YAML files still need to be authored.
2. Branch naming still needs to be frozen canonically.
3. Some authority/cutover modeling details are still implementation-open.
4. Pause/workflow event persistence is defined conceptually but not yet folded into the canonical DB/runtime docs.
5. Summary taxonomy and source-role taxonomy still need final implementation-grade normalization.
6. A few recently-added appendix decisions still need to be folded back into the core v2 specs.

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
