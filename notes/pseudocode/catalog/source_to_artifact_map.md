# Source To Artifact Map

## Purpose

This catalog maps the current `notes/*.md` corpus into pseudocode-compilation targets.

Use this file to decide:

- which notes are canonical inputs
- which notes are superseded references
- which notes should become modules, flows, state machines, or pseudotests
- which notes are review-only or gap-analysis inputs

---

## Classification keys

### Source status

- `canonical_v2`
- `revised_reference`
- `appendix`
- `planning`
- `origin`
- `analysis`

### Artifact class

- `module`
- `flow`
- `state_machine`
- `decision_table`
- `schema_rule`
- `coverage_input`

---

## Runtime and orchestration sources

| Source note | Status | Primary artifact class | Planned pseudocode targets |
| --- | --- | --- | --- |
| `notes/specs/runtime/runtime_command_loop_spec_v2.md` | `canonical_v2` | `flow` | `modules/run_node_loop.md`, `modules/execute_compiled_subtask.md`, `pseudotests/runtime_core_tests.md` |
| `notes/archive/superseded/runtime_command_loop_spec.md` | `revised_reference` | `coverage_input` | compare only where v2 looks underspecified |
| `notes/planning/expansion/runtime_pseudocode_plan.md` | `planning` | `coverage_input` | module inventory, source coverage checks |
| `notes/specs/runtime/node_lifecycle_spec_v2.md` | `canonical_v2` | `state_machine` | `state_machines/node_lifecycle.md`, runtime admission rules |
| `notes/archive/superseded/node_lifecycle_spec_revised.md` | `revised_reference` | `coverage_input` | fallback reference only |
| `notes/contracts/runtime/session_recovery_appendix.md` | `appendix` | `flow` | `modules/recover_interrupted_run.md`, recovery pseudotests |
| `notes/contracts/persistence/compile_failure_persistence.md` | `appendix` | `state_machine` | `modules/compile_workflow.md`, compile failure pseudotests |
| `notes/contracts/persistence/pause_workflow_event_persistence.md` | `appendix` | `state_machine` | pause event persistence rules, runtime tests |
| `notes/contracts/parent_child/parent_failure_decision_spec.md` | `appendix` | `decision_table` | parent escalation logic, failure state machine |
| `notes/contracts/parent_child/child_materialization_and_scheduling.md` | `appendix` | `flow` | child materialization and scheduling flows |
| `notes/contracts/parent_child/child_session_mergeback_contract.md` | `appendix` | `decision_table` | pushed child session return contract |
| `notes/contracts/runtime/invalid_dependency_graph_handling.md` | `appendix` | `decision_table` | dependency validator flow and pseudotests |
| `notes/contracts/parent_child/manual_vs_auto_tree_interaction.md` | `appendix` | `flow` | manual/auto reconciliation flow |
| `notes/contracts/runtime/runtime_environment_policy_note.md` | `appendix` | `decision_table` | optional environment setup module |
| `notes/catalogs/tuning/runtime_tuning_matrix.md` | `planning` | `decision_table` | placement rules only, not a first-pass module |

---

## Compilation and YAML sources

| Source note | Status | Primary artifact class | Planned pseudocode targets |
| --- | --- | --- | --- |
| `notes/specs/yaml/yaml_schemas_spec_v2.md` | `canonical_v2` | `schema_rule` | `modules/compile_workflow.md`, schema validation flow |
| `notes/archive/superseded/yaml_schemas_spec_revised.md` | `revised_reference` | `coverage_input` | fallback reference only |
| `notes/catalogs/inventory/yaml_inventory_v2.md` | `planning` | `coverage_input` | family inventory checks for source loading |
| `notes/catalogs/inventory/default_yaml_library_plan.md` | `planning` | `schema_rule` | default source-discovery expectations |
| `notes/contracts/yaml/override_conflict_semantics.md` | `appendix` | `decision_table` | override resolution branch logic |
| `notes/contracts/yaml/override_versioning_note.md` | `appendix` | `decision_table` | version/lineage follow-up rules |
| `notes/contracts/yaml/hook_expansion_algorithm.md` | `appendix` | `flow` | hook expansion submodule in compile pipeline |
| `notes/specs/architecture/code_vs_yaml_delineation.md` | `analysis` | `decision_table` | compile/runtime boundary guardrails |
| `notes/planning/expansion/review_testing_docs_yaml_plan.md` | `planning` | `schema_rule` | quality-gate stage generation rules |

---

## Database, authority, provenance, and audit sources

| Source note | Status | Primary artifact class | Planned pseudocode targets |
| --- | --- | --- | --- |
| `notes/specs/database/database_schema_spec_v2.md` | `canonical_v2` | `schema_rule` | durable writes sections across all modules |
| `notes/archive/superseded/database_schema_spec_revised.md` | `revised_reference` | `coverage_input` | fallback reference only |
| `notes/planning/expansion/database_schema_v2_expansion.md` | `planning` | `coverage_input` | implementation-grade durable write details |
| `notes/specs/architecture/authority_and_api_model.md` | `appendix` | `decision_table` | daemon authority guardrails on mutations |
| `notes/specs/provenance/provenance_identity_strategy.md` | `appendix` | `decision_table` | provenance update module |
| `notes/catalogs/audit/auditability_checklist.md` | `analysis` | `coverage_input` | audit completeness review for pseudotests |
| `notes/catalogs/vocabulary/state_value_catalog.md` | `appendix` | `schema_rule` | canonical enum vocabulary for states/results |
| `notes/contracts/runtime/cutover_policy_note.md` | `appendix` | `decision_table` | cutover timing and authoritative-version rules |

---

## CLI, automation, and operator-surface sources

| Source note | Status | Primary artifact class | Planned pseudocode targets |
| --- | --- | --- | --- |
| `notes/specs/cli/cli_surface_spec_v2.md` | `canonical_v2` | `flow` | CLI-visible expectations across modules and tests |
| `notes/archive/superseded/cli_surface_spec_revised.md` | `revised_reference` | `coverage_input` | fallback reference only |
| `notes/catalogs/traceability/action_automation_matrix.md` | `analysis` | `coverage_input` | automation coverage checks |
| `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md` | `planning` | `flow` | future example flow only |
| `notes/scenarios/walkthroughs/hypothetical_plan_workthrough.md` | `planning` | `flow` | future example flow only |

---

## Git, rebuild, and rectification sources

| Source note | Status | Primary artifact class | Planned pseudocode targets |
| --- | --- | --- | --- |
| `notes/specs/git/git_rectification_spec_v2.md` | `canonical_v2` | `flow` | rectification and rebuild modules |
| `notes/archive/superseded/git_rectification_spec_revised.md` | `revised_reference` | `coverage_input` | fallback reference only |
| `notes/planning/implementation/implementation_slicing_plan.md` | `planning` | `coverage_input` | implementation-order guidance only |

---

## Traceability, gap-analysis, and origin sources

| Source note | Status | Primary artifact class | Planned pseudocode targets |
| --- | --- | --- | --- |
| `notes/explorations/original_concept.md` | `origin` | `coverage_input` | high-level intent checks |
| `notes/planning/expansion/full_spec_expansion_plan.md` | `planning` | `coverage_input` | historical sequencing only |
| `notes/catalogs/inventory/major_feature_inventory.md` | `analysis` | `coverage_input` | feature coverage checks |
| `notes/catalogs/traceability/spec_traceability_matrix.md` | `analysis` | `coverage_input` | source coverage and gap review |
| `notes/catalogs/traceability/cross_spec_gap_matrix.md` | `analysis` | `coverage_input` | contradiction review and open questions |
| `notes/scenarios/journeys/common_user_journeys_analysis.md` | `analysis` | `flow` | future end-to-end flows |
| `notes/explorations/musings.md` | `origin` | `coverage_input` | optional idea reservoir, not canonical |

---

## First-pass canonical source set

The first implementation-facing pseudocode pass should treat these as canonical:

- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`

These appendices should be folded in immediately when writing modules:

- `notes/contracts/persistence/compile_failure_persistence.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `notes/contracts/yaml/override_conflict_semantics.md`
- `notes/contracts/yaml/hook_expansion_algorithm.md`
- `notes/contracts/parent_child/parent_failure_decision_spec.md`
- `notes/contracts/runtime/invalid_dependency_graph_handling.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/specs/provenance/provenance_identity_strategy.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/catalogs/vocabulary/state_value_catalog.md`

---

## First artifacts to author

1. `modules/compile_workflow.md`
2. `modules/run_node_loop.md`
3. `modules/execute_compiled_subtask.md`
4. `modules/handle_subtask_failure.md`
5. `modules/recover_interrupted_run.md`
6. `pseudotests/runtime_core_tests.md`

---

## Current gaps exposed by the map

- lifecycle, pause, and compile-failure state vocabularies still need to be normalized into one pseudocode-facing enum set
- some appendix decisions are authoritative in practice but not yet folded into all core v2 docs
- example user-flow notes should stay secondary until the runtime spine is explicit
- revised pre-v2 specs should not be used as primary sources unless a v2 gap is discovered
