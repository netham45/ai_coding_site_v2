# Phase UT-01: Batch Execution Groups

## Goal

Define the dependency-ordered batches used to raise the existing test suite to doctrine level without doing the work one feature at a time or all at once.

## Rationale

- Rationale: Many existing features imply that other features are already functioning, and their tests share the same runtime foundations, canonical commands, or durable-state assumptions.
- Reason for existence: This phase exists to make the hardening effort executable in sane waves that maximize reuse, minimize duplicated setup work, and prevent unstable half-updated proving narratives.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/update_tests/00_raise_existing_tests_to_doctrine_level.md`
- `plan/features/28_F23_testing_framework_integration.md`
- `plan/features/35_F36_auditable_history_and_reproducibility.md`
- `plan/features/57_F31_database_runtime_state_schema_family.md`
- `plan/features/58_F31_database_session_attempt_history_schema_family.md`
- `plan/features/59_F30_database_provenance_docs_audit_schema_family.md`
- `plan/features/69_F21_F22_F23_F29_turnkey_quality_gate_finalize_chain.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`
- `notes/planning/implementation/full_real_end_to_end_flow_hardening_plan.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`

## Scope

- Database: batch work by durable-state families rather than per-feature fragments.
- CLI: batch command families that share the same user-visible surfaces and proving commands.
- Daemon: batch runtime capability families that share orchestration prerequisites.
- YAML: batch compile and declarative-contract work by compiler/runtime stages.
- Prompts: batch prompt/history/runtime-prompt proof with the runtime families that actually exercise them.
- Notes: update notes and checklists at the end of each batch rather than leaving repo-wide drift until the very end.
- Tests: organize remediation around shared proving narratives instead of isolated feature slices.
- Performance: batch performance alignment after the relevant runtime families have been hardened.

## Execution Batches

### Batch A: Command And Revision Consistency

Purpose:

- normalize canonical commands
- reconcile migration-head expectations
- remove repo-surface contradictions before deeper hardening starts

Typical outputs:

- README/test command fixes
- migration-head expectation fixes
- checklist/notes command normalization

Acceptance gate:

- authoritative repo surfaces agree on the command set and current revision expectations
- `notes/catalogs/checklists/verification_command_catalog.md` is the canonical command source for later batches

### Batch B: Database-Truth Foundations

Purpose:

- raise all durable-state foundations to real persistence proof
- establish confidence in runtime-state, history, and DB view assertions

Included families:

- runtime state
- session/attempt history
- provenance/docs/audit DB families
- migration compatibility

Acceptance gate:

- no core database-backed feature remains effectively verified by unit-only proof

### Batch C: Core CLI And Daemon Surfaces

Purpose:

- raise the main operator and AI-facing command families to real boundary proof

Included families:

- workflow start/compile/show
- current state and blockers
- operator structure/history commands
- progress and stage transition commands

Acceptance gate:

- the main command loop and operator inspection surfaces are proven through CLI-to-daemon round trips

### Batch D: Compile, YAML, And Prompt Contracts

Purpose:

- raise declarative compile/runtime behavior from schema or helper proof to real compiler proof

Included families:

- source discovery
- schema validation
- override resolution
- hook/policy expansion
- rendering/freeze
- prompt selection/history where compile/runtime-linked

Acceptance gate:

- compile-stage families are proven through actual compiled outputs and diagnostics

### Batch E: Session, Recovery, And Runtime Coordination

Purpose:

- raise session ownership, recovery, stale-session, and control semantics as one coherent runtime family

Included families:

- session bind/attach/resume/control
- provider-agnostic and provider-specific recovery
- idle/nudge behavior
- tmux/session harness runtime behavior

Acceptance gate:

- recovery-sensitive features are proven through real runtime coordination rather than isolated helper logic

### Batch F: Child Scheduling, Reconciliation, And Failure Handling

Purpose:

- raise all multi-node coordination behavior together because these features depend heavily on each other

Included families:

- dependency admission
- child materialization and scheduling
- manual tree/hybrid authority
- child merge and reconciliation
- conflict surfacing
- parent failure decisions
- intervention matrix

Acceptance gate:

- child and parent coordination features are proven as one coherent runtime family instead of fragmented subcases

### Batch G: Quality, Docs, Provenance, And Audit

Purpose:

- raise the quality and audit plane together because the strongest proof requires a shared live-run narrative

Included families:

- validation
- review
- testing
- prompt history and summary history
- documentation generation
- provenance/rationale
- audit and reproducibility
- turnkey quality chain

Acceptance gate:

- the quality chain and resulting audit/provenance/docs surfaces are proven end to end through real runtime execution

### Batch H: Resilience And Recovery Hardening

Purpose:

- revisit all hardened families specifically for interruption, retry, restart, duplicate request, and impossible-wait behavior

Included families:

- interruption paths
- retry paths
- restart paths
- stale-session recovery
- duplicate/conflicting request handling
- impossible dependency waits

Acceptance gate:

- resilience requirements are proven across the already-hardened runtime families

### Batch I: Performance Alignment And Final Sweep

Purpose:

- align performance assertions with the now-hardened proof model
- run the canonical command set and publish the final state

Included families:

- performance harness cleanup
- threshold documentation
- final repo-surface reconciliation
- final hardening report

Acceptance gate:

- performance assumptions match current reality
- final documentation reflects actual verified status

## Batch Rules

- Do not open a later batch until the current batch has a stable proving command and updated notes.
- If a later-batch task exposes a blocker in an earlier batch, move the blocker back to the earlier batch instead of silently working around it.
- Batch completion must be documented explicitly before work proceeds.
- Cross-batch shortcuts are not allowed if they weaken the proving narrative for the earlier batch.

## Suggested Implementation Order

1. Batch A
2. Batch B
3. Batch C
4. Batch D
5. Batch E
6. Batch F
7. Batch G
8. Batch H
9. Batch I

## Exit Criteria

- the hardening effort is organized into reusable dependency-ordered waves
- each wave has a clear proving narrative and acceptance gate
- no feature family is forced into one-by-one or all-at-once remediation
