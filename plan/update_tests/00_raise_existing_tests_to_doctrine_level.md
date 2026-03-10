# Phase UT-00: Raise Existing Tests To Doctrine Level

## Goal

Raise the existing test suite so it proves all applicable system boundaries for current implemented behavior instead of primarily proving convenient in-memory or single-surface paths.

## Rationale

- Rationale: The repository already has broad unit, integration, flow, and performance coverage, but the updated doctrine now requires stronger proof that tests cover all affected systems where behavior is described as database-backed, CLI-visible, daemon-owned, YAML-driven, or prompt-bound.
- Reason for existence: This phase exists to harden verification quality for behavior that already exists or is already claimed as implemented, partial, or verified, without treating fast-path internal proof as sufficient when the real contract spans multiple systems.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/28_F23_testing_framework_integration.md`: F23 established the current test framework foundations that this hardening plan must build on rather than replace.
- `plan/features/35_F36_auditable_history_and_reproducibility.md`: F36 defines reconstructible audit expectations that must be proven through real durable boundaries.
- `plan/features/57_F31_database_runtime_state_schema_family.md`: runtime-state features must not be considered verified by non-durable proof.
- `plan/features/58_F31_database_session_attempt_history_schema_family.md`: session and attempt history claims require DB-backed verification.
- `plan/features/59_F30_database_provenance_docs_audit_schema_family.md`: provenance/docs/audit behavior must be proven through real persistence and inspectability paths.
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`: orchestration and result capture are especially sensitive to convenient fast-route testing.
- `plan/features/69_F21_F22_F23_F29_turnkey_quality_gate_finalize_chain.md`: quality-chain behavior must be raised to doctrine-level system coverage.
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`: rebuild/cutover coordination claims require durable and inspectable proof.
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`: git/finalize flows are high-value examples of real-boundary verification.
- `plan/features/72_F13_expanded_human_intervention_matrix.md`: intervention flows must be proven through their real operator/runtime surfaces.

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `notes/planning/implementation/full_real_end_to_end_flow_hardening_plan.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`
- `notes/planning/implementation/scenario_and_flow_pytest_plan.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`
- `notes/catalogs/audit/auditability_checklist.md`

## Scope

- Database: identify every currently implemented database-backed behavior that is only partially proven and add or strengthen tests so durable writes, reads, views, and migration/current-head assumptions are asserted through the real persistence layer where applicable.
- CLI: identify command families that currently have parser or internal proof only and add or strengthen tests so the user-facing contract is verified through the CLI boundary where applicable.
- Daemon: identify daemon-owned runtime, mutation, scheduling, recovery, and inspection behavior that is only internally proven and raise it to real daemon/API contract proof where applicable.
- YAML: identify YAML families that are only existence- or schema-validated and extend tests so declarative assets are proven through compile or runtime behavior where the product claims they matter.
- Prompts: identify prompt assets that are only existence- or render-tested and extend tests so prompt/runtime selection, delivery, or history behavior is proven where applicable.
- Notes: update README, notes, checklists, and flow coverage docs so canonical verification commands, completion labels, and current support levels match actual runnable proof.
- Tests: add or revise unit, integration, flow, resilience, and performance tests at the proper layers; do not remove fast tests that remain valuable, but do not allow them to stand in for required real-boundary proof.
- Performance: verify that performance tests align with current implemented surfaces, current migration head, and current doctrine expectations.

## Deliverables

- a system-coverage audit for the existing tests
- a gap list showing where existing proof relies on the convenient fast route
- canonical verification commands for the current test and hardening surfaces
- a batch-execution plan that groups remediation work by shared prerequisites and dependency order
- new or revised tests that prove affected database/CLI/daemon/YAML/prompt boundaries where currently missing
- updated notes, checklists, and README entries that match actual runnable verification commands
- a final hardening report stating what is implemented, verified, partial, flow-complete, or intentionally deferred

## Phases

### Phase 1: Coverage Audit

- inventory all current test files under `tests/`
- map major implemented surfaces to affected systems: database, CLI, daemon, YAML, prompts
- record the current proving layer for each surface
- record where the current proof relies on the convenient fast route
- record the current canonical command, if any
- classify each audited area as `implemented`, `verified`, `partial`, or `flow-complete`

Acceptance criteria:

- every major implemented subsystem has an audit row
- every row explicitly names affected systems
- every row identifies missing proving layers or shortcut-only proof

### Phase 2: Canonical Command Normalization

- establish a canonical command set for bootstrap, migrations, unit tests, integration tests, flow suites, YAML flow-asset suites, performance tests, and real E2E tests where applicable
- reconcile command mismatches across `README.md`, notes, checklists, flow docs, and CI assumptions
- ensure commands are runnable from a clean shell without rediscovery
- document env assumptions explicitly where commands depend on them

Acceptance criteria:

- authoritative repo surfaces do not disagree on the proving command for the same scope
- every claimed verified surface has a written canonical command
- commands no longer depend on unstated shell knowledge

### Phase 3: Database-Truth Hardening

- identify database-backed behaviors currently proven only through internal or non-durable tests
- raise runtime-state, run-history, prompt-history, summary-history, provenance/docs/audit, rebuild/cutover, and migration-head proof to real DB-backed verification where applicable
- assert durable writes and follow-up reads rather than only internal state transitions
- assert DB views/history surfaces where the product claims inspectability

Acceptance criteria:

- no important database-backed feature is considered verified by unit-only proof
- durable state changes are asserted through real DB-backed flows where applicable
- migration-head expectations are internally consistent across repo surfaces

### Phase 4: CLI/Daemon Boundary Hardening

- identify CLI-visible features that currently have parser or direct-helper proof only
- identify daemon-owned behaviors that currently bypass the real CLI/daemon contract in their highest-value proof
- add or strengthen integration tests that round-trip through CLI and daemon boundaries for operator-visible behaviors
- verify structured failure output and operator inspection surfaces

Acceptance criteria:

- important user-visible command families are not considered verified by parser tests alone
- critical operational flows have CLI-to-daemon round-trip proof
- failure surfaces are stable and inspectable

### Phase 5: YAML And Prompt Contract Hardening

- identify YAML families currently proven only by schema validation or file presence
- identify prompt assets currently proven only by existence or rendering
- extend compile/runtime tests so YAML effects are proven through actual compiler/runtime behavior where claimed
- prove prompt selection, delivery, and/or history behavior where the product claims those contracts matter

Acceptance criteria:

- YAML is not considered verified only because schema validation passes
- prompts are not considered verified only because files exist and render
- declarative assets are proven through actual compiler/runtime behavior where applicable

### Phase 6: Flow Hardening Against Doctrine

- review each canonical flow and list affected systems
- confirm the actual current support level for each flow
- verify that the documented proving command actually demonstrates the claimed support level
- prioritize partial flows first: Flow 04, Flow 08, Flow 09, Flow 10, Flow 13
- revisit any `full` flow whose strongest proof still avoids an affected system boundary

Acceptance criteria:

- flow labels match actual proving strength
- flow coverage docs do not overstate completion
- each flow’s documented command proves the level it claims

### Phase 7: Resilience And Recovery Hardening

- identify current gaps in interruption, retry, restart, stale-session, duplicate-request, impossible-wait, and recovery-proof coverage
- add or strengthen resilience tests where doctrine-required recovery semantics are currently under-proven
- ensure failure and recovery state are inspectable through intended surfaces

Acceptance criteria:

- recovery-sensitive features are not considered verified without resilience proof
- retry and recovery behavior are proven through real durable or API-visible boundaries where applicable
- audit trails after failure are asserted, not inferred

### Phase 8: Performance And Budget Alignment

- review current performance tests against current implemented surfaces
- remove stale assumptions such as outdated migration-head expectations
- add missing performance coverage for high-frequency DB-backed inspection or compile/runtime paths where doctrine expectations require it
- document thresholds where performance-sensitive paths are intentionally budgeted

Acceptance criteria:

- performance checks align with current repo head and current implemented surfaces
- thresholds are intentional and documented where applicable
- no stale performance assertion contradicts current repo state

### Phase 9: Final Verification Sweep

- run the canonical hardening command set
- record pass/fail results
- record remaining partial or deferred areas
- update notes/checklists/README/flow coverage docs to match the verified state
- produce a final hardening report that distinguishes `implemented` from `verified` and `flow-complete`

Acceptance criteria:

- canonical command references are current
- doctrine-relevant existing tests are raised to the correct system-coverage level or explicitly documented as still partial
- the final hardening report can state what is actually verified today without ambiguity

## Batch Execution Rule

This hardening work must not be executed feature by feature in isolation and must not be attempted as one monolithic repo-wide rewrite.

The correct execution model is batch-based.

Each batch should:

- group features that share prerequisites, runtime boundaries, or proving commands
- raise a coherent capability family together
- produce one stable proving narrative for that family
- stop for verification before the next batch begins

Batching is required because many features imply or depend on other features working first. Raising one feature's tests in isolation can create duplicated setup work, unstable proving commands, or misleading partial coverage.

Use dependency-ordered batches such as:

- command and migration consistency
- database-truth foundations
- core CLI and daemon boundary proof
- compile/YAML/prompt contract proof
- session/recovery/runtime coordination proof
- child scheduling/reconciliation/failure proof
- quality/docs/provenance/audit proof
- resilience and recovery hardening
- performance alignment

The detailed grouping and order lives in `plan/update_tests/01_batch_execution_groups.md`.

## Suggested Task Slicing

Break this work into batch-scoped tasks, each with its own test updates and note updates.

Recommended slice pattern:

- one dependency-ordered batch at a time
- within a batch, one coherent capability family per task
- one resilience category per task where resilience is the batch focus
- one performance family per task where performance is the batch focus

Good slice examples:

- align migration-head expectations and verification commands across repo surfaces
- raise the whole session recovery capability family to real DB-backed proof
- raise the whole quality-chain capability family to prove the full affected-system path
- raise provenance/docs tests to durable audit proof
- raise the CLI operator inspection family to real round-trip proof
- harden the partial-flow family containing Flow 04, Flow 08, Flow 09, Flow 10, and Flow 13

## Required Evidence Per Task

Every task created from this plan should include:

- affected systems
- current gap
- intended proving layer
- canonical proving command
- exact files expected to change
- exact notes/checklists expected to change
- the status claim that becomes valid after completion

## Canonical Questions For Each Remediation Task

1. Which of the five systems are affected by the described behavior?
2. Which of those systems are currently unproven or only proven through a shortcut?
3. What is the lowest test layer that can prove the missing behavior clearly?
4. What higher-layer test is still required because the boundary itself matters?
5. What durable records, audit outputs, or recovery semantics must be asserted?
6. What command proves this work without rediscovery?
7. What note/checklist/flow claim must change with the code and tests?

## Exit Criteria

This hardening phase is complete when:

- every major implemented behavior has an explicit affected-systems mapping
- no important database-backed behavior is considered verified by unit-only proof
- no important CLI or daemon contract is considered verified by internal-only proof
- no important YAML or prompt contract is considered verified by existence-only proof
- canonical verification commands are consistent across repo surfaces
- flow status labels match actual proving strength
- remaining partial or deferred areas are documented plainly
- the final hardening report can name what is actually verified today without ambiguity

Interpretation rule:

- this exit criterion is for the hardening plan slice itself
- it does not override the canonical feature-status, command, or execution-policy surfaces
- final implementation and release claims still belong in the checklist layer
