# Full Epic Tree Real E2E Plan

## Goal

Create real end-to-end tests that start from one epic and prove this full hierarchy narrative through real code:

- create a top-level epic
- decompose the epic into phases
- decompose phases into plans
- decompose plans into tasks
- execute task nodes through the real AI-facing runtime path
- merge child results back up through plan, phase, and epic reconciliation
- modify one already-merged phase
- unmerge or supersede the affected phase lineage from that phase upward
- regenerate from the changed phase back down to plans and tasks
- re-run the affected child work
- re-merge the regenerated lineage back up to the epic
- verify durable audit, lineage, rebuild, and inspectability surfaces at each stage

## Rationale

- Rationale: The current real-E2E checkpoints prove only isolated flow slices. They do not yet prove one uninterrupted hierarchy narrative from epic creation through child execution and merge-back.
- Reason for existence: This plan exists to make the core orchestration claim testable as one real system story instead of a stitched set of partial flow proofs.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`
- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/contracts/parent_child/child_session_mergeback_contract.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/planning/implementation/full_real_end_to_end_flow_hardening_plan.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`

## Scope

- Database: verify durable hierarchy rows, node versions, workflows, runs, lifecycle states, merge events, summaries, quality results, and rebuild/audit artifacts across the full tree narrative.
- CLI: drive the narrative through real CLI subprocess commands wherever a user or AI session would actually interact with the system.
- Daemon: require the real daemon subprocess to own orchestration, admission, scheduling, run progress, reconciliation, and finalize behavior.
- YAML: exercise the shipped built-in hierarchy, task ladders, layouts, and quality/runtime policies through actual compile and runtime behavior.
- Prompts: exercise real prompt selection and delivery for decomposition and execution stages, not just file existence or static rendering.
- Notes: keep expected-failure posture, covered stages, and gaps documented honestly while the suite is being brought up.
- Tests: add one full narrative suite plus per-stage assertions that can fail independently without hiding the broader missing-runtime picture.
- Performance: not the main proving goal of this plan, but the suite should remain serializable and diagnostically usable.

## Primary Narrative Under Test

The primary intended narrative is:

1. start one parentless epic
2. compile and admit the epic
3. run epic decomposition until phase children exist
4. run each phase until plan children exist
5. run each plan until task children exist
6. run each task through real execution and gate progression
7. wait for child completion at each parent
8. reconcile task outputs into the parent plan
9. reconcile plan outputs into the parent phase
10. reconcile phase outputs into the parent epic
11. inspect the completed authoritative tree state
12. change one merged phase and create a new candidate lineage from that phase
13. prove the old merged phase lineage is no longer the authoritative active path for the changed scope
14. regenerate the changed phase downward into plans and tasks
15. re-run the affected plan and task work through the real runtime path
16. rebuild upward from the changed phase toward the epic
17. re-merge the rebuilt lineage back into the epic
18. inspect the final authoritative tree, rebuild history, merge history, summaries, and audit state

## Test Posture

This suite is expected to fail initially.

That failure posture is deliberate and required.

The first implementation pass should not weaken the suite to match current limitations. Instead, the suite should record which missing runtime capabilities prevent the full narrative from completing.

Expected early failure classes include:

- top-level hierarchy restrictions still narrower than doctrine
- built-in default ladders not yet performing the full decomposition chain automatically
- task execution not yet driven by a real provider-backed or harness-backed AI step for the full hierarchy story
- merge/reconcile/finalize behavior still incomplete in one or more parent layers
- phase-level rectification and upstream rebuild behavior still incomplete for a real merged-tree rewrite narrative
- audit and inspection surfaces missing one or more durable assertions needed for full-tree proof

## Proposed Test Files

Primary narrative suite:

- `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`

Optional helper or split suites if the single file becomes too large:

- `tests/e2e/test_e2e_full_epic_tree_stage_decomposition_real.py`
- `tests/e2e/test_e2e_full_epic_tree_stage_execution_real.py`
- `tests/e2e/test_e2e_full_epic_tree_stage_mergeback_real.py`

The primary suite remains the authoritative proof target. Split files are only acceptable if they preserve one explicit feature-to-narrative mapping and do not dilute the claim.

## Required Stage Coverage

### Stage 1: Epic startup

Assertions:

- epic node is created durably
- workflow compiles durably
- initial run is admitted durably
- current workflow/task/subtask inspection is coherent

### Stage 2: Epic to phase decomposition

Assertions:

- the epic creates durable phase children through real runtime work
- phase lineage, hierarchy edges, and child scheduling state are inspectable
- the epic enters the correct waiting or progression state

### Stage 3: Phase to plan decomposition

Assertions:

- at least one phase creates durable plan children
- plan nodes inherit inspectable compiled workflows and lifecycle rows
- parent/child dependency state remains queryable

### Stage 4: Plan to task decomposition

Assertions:

- at least one plan creates durable task children
- task nodes are materialized from the real parent flow, not synthetic setup
- task acceptance and execution context are inspectable

### Stage 5: Task execution

Assertions:

- task runs advance through the real AI-facing or provider-backed runtime path
- prompts/context/attempt history/summaries are durably recorded
- task outputs become available for validation/review/testing/finalization where applicable

### Stage 6: Task-to-plan mergeback

Assertions:

- completed task outputs are collected by the parent plan
- plan reconciliation/merge records are durable and inspectable
- parent state changes reflect actual child completion rather than direct DB shortcuts

### Stage 7: Plan-to-phase mergeback

Assertions:

- completed plan outputs reconcile into the phase
- merge ordering, parent summaries, and resulting branch/history state are inspectable

### Stage 8: Phase-to-epic mergeback

Assertions:

- completed phase outputs reconcile into the epic
- final epic state reflects the real child lineage, not a simulated collapse

### Stage 9: Final inspectability

Assertions:

- `tree show` reflects the full hierarchy state
- node/run/workflow history is queryable at all tested levels
- summaries, prompts, provenance, merge, and docs surfaces remain inspectable after completion

### Stage 10: Phase modification after merge

Assertions:

- one already-merged phase is modified through the supported change or regeneration surface
- the system records a new candidate or superseding lineage for that phase
- the prior merged path remains inspectable as prior history rather than silently disappearing

### Stage 11: Phase unmerge and downward regeneration

Assertions:

- the affected phase no longer reuses the stale authoritative child tree for the changed scope
- new plan and task descendants are generated under the changed phase lineage
- rebuild history records the changed scope and resulting descendant regeneration

### Stage 12: Re-execution of regenerated tasks

Assertions:

- regenerated task nodes run through the real execution path
- new summaries, attempts, and outputs are recorded distinctly from the superseded lineage

### Stage 13: Rebuild and re-merge to epic

Assertions:

- the changed phase is rebuilt upward through its parent chain
- merge/reconcile records show the replacement of the old lineage by the rebuilt one
- authoritative/current-version reads point at the rebuilt lineage only after the required rebuild path is stable

### Stage 14: Post-rectification inspectability

Assertions:

- the final tree shows the rebuilt authoritative path
- rebuild history, merge history, workflow events, and lineage inspection can explain what changed
- operators can distinguish superseded lineage from current lineage at phase, plan, and task depth

## Prohibited Shortcuts

- no direct DB mutations to create children or mark them complete
- no synthetic prompt, summary, or result injection in place of the runtime path being claimed
- no in-process daemon bridge as the only proof
- no fake mergeback in place of real child reconciliation behavior
- no file-presence-only assertions where durable state or CLI/API inspection is part of the claim

## Harness Requirements

- real PostgreSQL-backed state
- real daemon subprocess
- real CLI subprocess commands
- isolated temp repo/workspace per test
- real git operations
- real session/runtime orchestration
- real AI-provider or explicitly documented real session harness behavior for the execution steps being claimed

## Feature Mapping

This narrative should explicitly cover, at minimum:

- configurable hierarchy
- workflow startup
- child spawning and scheduling
- node run orchestration
- AI-facing CLI/runtime progression
- child merge and reconciliation
- regeneration and upstream rectification
- cutover and authoritative-lineage selection
- live finalize/merge execution
- provenance/docs/audit readback

## Canonical Verification Commands

Plan/document consistency after adding this plan:

```bash
python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_verification_command_docs.py tests/unit/test_notes_quickstart_docs.py -q
```

Future suite command once the test file exists:

```bash
python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q
```

If the suite is split, add each concrete command to `notes/catalogs/checklists/verification_command_catalog.md` in the same change that introduces the tests.

## Phase Plan

### Phase 1: Define the full-tree narrative contract

- write the test narrative and stage assertions
- map each stage to existing flow and feature docs
- mark the suite explicitly as expected-to-fail until runtime catches up

### Phase 2: Build the epic-tree E2E harness path

- extend the current real-E2E harness so one test can manage a full tree lifecycle
- support deterministic waiting and inspection across parent and child nodes
- capture rich failure diagnostics when a stage stalls or diverges

### Phase 3: Land the first failing test skeleton

- add the real test file
- mark it with the required real-E2E markers
- let it fail on the first missing runtime barrier instead of weakening the scenario

### Phase 4: Expand from first barrier to full decomposition

- close the runtime gaps that block epic -> phase -> plan -> task creation
- rerun the same suite after each runtime change
- keep notes aligned with each newly exposed limitation

### Phase 5: Expand through execution and mergeback

- close the runtime gaps that block real task execution, parent waits, reconciliation, and finalize behavior
- add final-tree and audit assertions once the narrative reaches completion

### Phase 6: Expand through post-merge phase modification and rebuild

- close the runtime gaps that block modifying one merged phase
- prove unmerge or supersession semantics for the changed phase scope
- close the runtime gaps that block regenerating from the changed phase down to tasks
- close the runtime gaps that block rebuilding and re-merging the changed lineage back to the epic

## Exit Criteria

This plan is complete only when:

1. the full narrative suite exists in `tests/e2e/`
2. the suite runs through real daemon, CLI, DB, git, and session boundaries
3. the suite proves the hierarchy from epic down to task and back up through mergeback
4. the suite then proves phase modification, unmerge or supersession, downward regeneration, and re-merge to the epic
5. any remaining red stage is documented as a concrete runtime gap rather than hidden behind weaker assertions
6. the canonical verification command is recorded in `verification_command_catalog.md`

## Known Initial Status

- status: `planned`
- expected initial test result: `failing`
- reason the first red state is acceptable: the current repository does not yet prove one uninterrupted epic-to-task-to-mergeback-to-phase-rectification runtime narrative through real E2E
