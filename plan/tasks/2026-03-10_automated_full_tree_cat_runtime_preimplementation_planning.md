# Task: Automated Full-Tree Cat Runtime Preimplementation Planning

## Goal

Create the missing planning and note surface for the automated full-tree `cat` runtime narrative before any runtime implementation work continues.

## Rationale

- Rationale: The repository does not yet have a settled design package for this exact narrative.
- Reason for existence: Child materialization, child auto-run, scoped parent decomposition, and the final E2E are all still underdefined for this requested flow, so coding before those notes exist would likely produce the wrong runtime behavior.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/35_F35_project_policy_extensibility.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`
- `plan/tasks/2026-03-10_automated_full_tree_cat_runtime_e2e.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`
- `plan/reconcilliation/02_full_epic_tree_real_e2e_plan.md`

## Scope

- Database: define what durable state and audit evidence must exist at each hierarchy tier for this narrative.
- CLI: define the canonical AI/operator command flow required for automated decomposition and completion.
- Daemon: define the runtime ownership boundaries, background automation rules, and sequencing expectations for parent and child work.
- YAML: define whether this narrative uses built-in defaults, scoped overrides, workflow profiles, or project policy.
- Prompts: define the parent and leaf prompt contract needed for the automated `cat` narrative.
- Tests: define the bounded-to-E2E proving ladder and explicit feature-to-flow mapping.
- Performance: define acceptable scope/budgets for the real E2E so the flow remains debuggable.
- Notes: create or update the missing design documents before implementation resumes.

## Plan

### Phase 0A: Narrative and invariants

1. Write the exact automated hierarchy flow from epic through leaf completion.
2. Document the invariants for:
   - generated layout authority
   - child auto-start eligibility
   - scoped parent decomposition selection
   - durable proof checkpoints at epic, phase, plan, and task depth

Exit criteria:

- there is a clear narrative and invariant set for the requested flow

### Phase 0B: Coverage and proving map

1. Define which existing flow/checklist/spec documents must be updated.
2. Define the phased proving ladder:
   - planning/spec completion
   - bounded runtime proofs
   - final real E2E
3. Map the automated `cat` narrative to feature/checklist/flow coverage surfaces.

Exit criteria:

- the repo has an explicit proving and traceability map for this narrative

### Phase 0C: Handoff into implementation phases

1. Update the umbrella task plan to gate later runtime work on this planning task.
2. Record the remaining runtime phases as blocked on this note batch.

Exit criteria:

- no later runtime phase can honestly start without the planning surface existing first

## Verification

- `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- The repository has a dedicated preimplementation plan for the automated full-tree `cat` narrative.
- The missing note/flow/checklist surfaces to create are explicit.
- Later implementation phases are clearly gated on this planning batch.
