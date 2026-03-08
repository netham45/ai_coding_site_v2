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
| `notes/runtime_command_loop_spec_v2.md` | `canonical_v2` | `flow` | `modules/run_node_loop.md`, `modules/execute_compiled_subtask.md`, `pseudotests/runtime_core_tests.md` |
| `notes/runtime_command_loop_spec.md` | `revised_reference` | `coverage_input` | compare only where v2 looks underspecified |
| `notes/runtime_pseudocode_plan.md` | `planning` | `coverage_input` | module inventory, source coverage checks |
| `notes/node_lifecycle_spec_v2.md` | `canonical_v2` | `state_machine` | `state_machines/node_lifecycle.md`, runtime admission rules |
| `notes/node_lifecycle_spec_revised.md` | `revised_reference` | `coverage_input` | fallback reference only |
| `notes/session_recovery_appendix.md` | `appendix` | `flow` | `modules/recover_interrupted_run.md`, recovery pseudotests |
| `notes/compile_failure_persistence.md` | `appendix` | `state_machine` | `modules/compile_workflow.md`, compile failure pseudotests |
| `notes/pause_workflow_event_persistence.md` | `appendix` | `state_machine` | pause event persistence rules, runtime tests |
| `notes/parent_failure_decision_spec.md` | `appendix` | `decision_table` | parent escalation logic, failure state machine |
| `notes/child_materialization_and_scheduling.md` | `appendix` | `flow` | child materialization and scheduling flows |
| `notes/child_session_mergeback_contract.md` | `appendix` | `decision_table` | pushed child session return contract |
| `notes/invalid_dependency_graph_handling.md` | `appendix` | `decision_table` | dependency validator flow and pseudotests |
| `notes/manual_vs_auto_tree_interaction.md` | `appendix` | `flow` | manual/auto reconciliation flow |
| `notes/runtime_environment_policy_note.md` | `appendix` | `decision_table` | optional environment setup module |
| `notes/runtime_tuning_matrix.md` | `planning` | `decision_table` | placement rules only, not a first-pass module |

---

## Compilation and YAML sources

| Source note | Status | Primary artifact class | Planned pseudocode targets |
| --- | --- | --- | --- |
| `notes/yaml_schemas_spec_v2.md` | `canonical_v2` | `schema_rule` | `modules/compile_workflow.md`, schema validation flow |
| `notes/yaml_schemas_spec_revised.md` | `revised_reference` | `coverage_input` | fallback reference only |
| `notes/yaml_inventory_v2.md` | `planning` | `coverage_input` | family inventory checks for source loading |
| `notes/default_yaml_library_plan.md` | `planning` | `schema_rule` | default source-discovery expectations |
| `notes/override_conflict_semantics.md` | `appendix` | `decision_table` | override resolution branch logic |
| `notes/override_versioning_note.md` | `appendix` | `decision_table` | version/lineage follow-up rules |
| `notes/hook_expansion_algorithm.md` | `appendix` | `flow` | hook expansion submodule in compile pipeline |
| `notes/code_vs_yaml_delineation.md` | `analysis` | `decision_table` | compile/runtime boundary guardrails |
| `notes/review_testing_docs_yaml_plan.md` | `planning` | `schema_rule` | quality-gate stage generation rules |

---

## Database, authority, provenance, and audit sources

| Source note | Status | Primary artifact class | Planned pseudocode targets |
| --- | --- | --- | --- |
| `notes/database_schema_spec_v2.md` | `canonical_v2` | `schema_rule` | durable writes sections across all modules |
| `notes/database_schema_spec_revised.md` | `revised_reference` | `coverage_input` | fallback reference only |
| `notes/database_schema_v2_expansion.md` | `planning` | `coverage_input` | implementation-grade durable write details |
| `notes/authority_and_api_model.md` | `appendix` | `decision_table` | daemon authority guardrails on mutations |
| `notes/provenance_identity_strategy.md` | `appendix` | `decision_table` | provenance update module |
| `notes/auditability_checklist.md` | `analysis` | `coverage_input` | audit completeness review for pseudotests |
| `notes/state_value_catalog.md` | `appendix` | `schema_rule` | canonical enum vocabulary for states/results |
| `notes/cutover_policy_note.md` | `appendix` | `decision_table` | cutover timing and authoritative-version rules |

---

## CLI, automation, and operator-surface sources

| Source note | Status | Primary artifact class | Planned pseudocode targets |
| --- | --- | --- | --- |
| `notes/cli_surface_spec_v2.md` | `canonical_v2` | `flow` | CLI-visible expectations across modules and tests |
| `notes/cli_surface_spec_revised.md` | `revised_reference` | `coverage_input` | fallback reference only |
| `notes/action_automation_matrix.md` | `analysis` | `coverage_input` | automation coverage checks |
| `notes/getting_started_hypothetical_task_guide.md` | `planning` | `flow` | future example flow only |
| `notes/hypothetical_plan_workthrough.md` | `planning` | `flow` | future example flow only |

---

## Git, rebuild, and rectification sources

| Source note | Status | Primary artifact class | Planned pseudocode targets |
| --- | --- | --- | --- |
| `notes/git_rectification_spec_v2.md` | `canonical_v2` | `flow` | rectification and rebuild modules |
| `notes/git_rectification_spec_revised.md` | `revised_reference` | `coverage_input` | fallback reference only |
| `notes/implementation_slicing_plan.md` | `planning` | `coverage_input` | implementation-order guidance only |

---

## Traceability, gap-analysis, and origin sources

| Source note | Status | Primary artifact class | Planned pseudocode targets |
| --- | --- | --- | --- |
| `notes/original_concept.md` | `origin` | `coverage_input` | high-level intent checks |
| `notes/full_spec_expansion_plan.md` | `planning` | `coverage_input` | historical sequencing only |
| `notes/major_feature_inventory.md` | `analysis` | `coverage_input` | feature coverage checks |
| `notes/spec_traceability_matrix.md` | `analysis` | `coverage_input` | source coverage and gap review |
| `notes/cross_spec_gap_matrix.md` | `analysis` | `coverage_input` | contradiction review and open questions |
| `notes/common_user_journeys_analysis.md` | `analysis` | `flow` | future end-to-end flows |
| `notes/musings.md` | `origin` | `coverage_input` | optional idea reservoir, not canonical |

---

## First-pass canonical source set

The first implementation-facing pseudocode pass should treat these as canonical:

- `notes/yaml_schemas_spec_v2.md`
- `notes/database_schema_spec_v2.md`
- `notes/node_lifecycle_spec_v2.md`
- `notes/runtime_command_loop_spec_v2.md`
- `notes/cli_surface_spec_v2.md`
- `notes/git_rectification_spec_v2.md`

These appendices should be folded in immediately when writing modules:

- `notes/compile_failure_persistence.md`
- `notes/session_recovery_appendix.md`
- `notes/override_conflict_semantics.md`
- `notes/hook_expansion_algorithm.md`
- `notes/parent_failure_decision_spec.md`
- `notes/invalid_dependency_graph_handling.md`
- `notes/child_materialization_and_scheduling.md`
- `notes/provenance_identity_strategy.md`
- `notes/cutover_policy_note.md`
- `notes/state_value_catalog.md`

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
