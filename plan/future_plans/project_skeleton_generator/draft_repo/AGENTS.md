# AGENTS.md

## Purpose

This repository is being built as a spec-driven system.

Work in this repo must stay aligned with the design notes and authoritative note assets in `notes/`.
Implementation is not allowed to drift away from the notes silently.

If coding reveals a limitation, contradiction, missing behavior, needed elaboration, verification gap, runtime mismatch, command inconsistency, checklist mismatch, or lifecycle-stage mismatch, the relevant note, checklist, plan, or lifecycle artifact must be updated in the same change or in an immediately adjacent follow-up change.

This repository does not permit undocumented behavior, undocumented verification steps, undocumented operational assumptions, silent narrowing of behavior to a more convenient implementation path, or completion claims that exceed the actual proving level.

## Lifecycle Governance Rule

Before meaningful work begins, read:

- `notes/lifecycle/00_project_lifecycle_overview.md`
- the current lifecycle stage note under `notes/lifecycle/`
- `plan/checklists/00_project_operational_state.md`

Follow the rules for the lifecycle stage the repository is actually in.

Treat stage-specific requirements as belonging to the lifecycle notes and operational-state checklist, not as ad hoc process rules to invent from memory.

Do not claim statuses or proving levels that the current stage and its completed sub-steps do not justify.

## Core Implementation Model

Every feature must be considered across the repository's declared primary systems.

No feature is complete until its effect on all applicable systems has been considered explicitly.

The default starter systems for this repository are:

### 1. Database

The database is the durable source of truth for state, lineage, history, and recovery-critical records.

### 2. CLI

The CLI is the operational interface for both human operators and AI sessions.

### 3. Daemon Or Backend

The daemon or backend is the live runtime authority.

### 4. Config Or YAML

Config assets define declarative structure and policy, but they must not silently absorb live runtime authority that belongs in code.

### 5. Prompts

Prompts are first-class implementation assets when AI behavior is part of the product or development workflow.

### 6. Website UI

The website UI is the browser operator surface when the product includes one.

If a starter project truly does not use one of these systems, mark that system explicitly as `not_applicable` in the governing plan, checklist, or review context.

## Stack Declaration Rule

This starter repository is intentionally language, framework, and toolkit agnostic.

Primary stack decisions belong to genesis and architecture work, not to the starter `AGENTS.md`.

Before setup or feature work claims a stable foundation, the repository should declare its chosen stack in the relevant notes, such as:

- `notes/catalogs/inventory/system_inventory.md`
- `notes/specs/architecture/code_vs_config_delineation.md`
- `notes/specs/architecture/authority_and_api_model.md`

## System Coverage Rule

Tests must cover all applicable systems touched by a feature, flow, or contract.

It is not acceptable to test only the most convenient or fastest surface when the described behavior spans multiple systems.

If one of the declared systems is truly not affected, that must be a deliberate conclusion recorded in the governing artifact for the work.

## Task Plan Rule

No meaningful code or process change should happen without a governing task plan under `plan/tasks/`.

Task plans must include:

- the goal
- the scope
- affected systems
- relevant notes
- canonical verification commands
- intended proof layer

## Development Operation Logging Rule

All meaningful work must leave a durable development log under `notes/logs/`.

Development logs must record:

- what was attempted
- what changed
- what commands and tests were run
- what passed or failed
- what remains blocked, deferred, or partial

## System Invariants Rule

Every meaningful subsystem must have explicit invariants documented in `notes/` or another approved design artifact.

Tests must defend invariants, not only features.

If implementation depends on an invariant that has not been written down yet, the work is incomplete.

## Checklist Enforcement Rule

Every meaningful feature must have a checklist entry that tracks implementation and verification status across all affected systems.

Checklists must explicitly record:

- affected systems
- implementation status
- bounded test status
- E2E status
- notes status
- known limitations
- overall status

If a system is not affected, mark it explicitly rather than omitting it.

## Checklist Maintenance Rule

Checklists are part of the implementation surface.

They must be updated whenever:

- code changes affect a tracked feature
- test status changes
- E2E status changes
- canonical commands change
- a new limitation is discovered
- the overall feature status changes

## Authoritative Document Rule

Authoritative document families are part of the implementation surface.

If a document family is authoritative, it must have automated consistency tests that enforce:

- required sections
- allowed status vocabularies
- required mappings
- required references
- family-specific invariants

Whenever an authoritative document changes, run the relevant document consistency tests afterward.

## Notes Maintenance Rule

The notes and authoritative note assets in `notes/` are part of the implementation surface.

They must be updated whenever work reveals:

- a limitation in the current design
- an ambiguity that must be resolved
- a contradiction between notes
- a new invariant
- a newly discovered failure mode
- a new recovery or concurrency constraint
- a testing expectation change
- a verification-command change
- a checklist or lifecycle mismatch

## Relevant Flow Rule

Relevant user and operator flows must be tracked through:

- narrative flow notes or walkthroughs
- a structured flow inventory when the repo adopts one

If implementation changes a relevant flow materially, update both surfaces together.

## Canonical Verification Command Rule

Build, test, validation, migration, flow, audit, and performance commands must be explicitly documented.

Do not rediscover proving commands ad hoc during implementation.

If a note or checklist claims something is verified, it must cite the documented canonical command that actually passed.

## Test Progression Rule

Testing must progress in stages.

### Stage 1: Bounded Proof

Bounded, simulated, mocked, or fixture-assisted tests are required during implementation and review.

### Stage 2: Real End-To-End Proof

Features intended to exist in real runtime usage must progress to full real E2E proof through the relevant system boundaries.

Bounded tests do not count as final completion proof for real runtime behavior.

## E2E Coverage Rule

Every meaningful feature must map to at least one explicit real E2E test target.

Grouped E2E narratives are acceptable, but traceability is still required.

If the strongest proof still bypasses the core runtime boundary being claimed, the feature is not E2E-covered.

## Completion Standard

No feature or change is complete without tests.

A feature is complete only when all of the following are true:

- relevant notes are current
- implementation matches the notes
- invariants are explicit
- affected systems are explicitly accounted for
- the feature checklist is current
- required development logs are current
- required bounded tests exist
- required real E2E tests exist for the intended scope
- required document consistency tests exist for changed authoritative document families
- canonical verification commands are documented
- those commands were actually run for the claimed layer
- known limitations are documented explicitly

## Completion State Vocabulary

Use these terms deliberately:

- `implemented`: assets or code exist, but stronger proof may still be missing
- `verified`: the documented verification command for the claimed layer actually passed
- `partial`: some intended behavior exists, but limitations or missing proving layers remain
- `flow_complete`: the intended user or operator flow passed end to end for the declared scope
- `release_ready`: all required bounded tests, real E2E tests, readiness docs, and checks are complete for the declared release scope

Do not describe work as complete if it is only implemented.

## Testing Standard

Tests must be written at the correct layer and remain parallel-safe when their required capabilities are present.

Test categories include:

- unit and bounded tests
- integration tests
- end-to-end tests
- document consistency tests
- performance tests
- resilience tests

If a test passes only when run serially because of shared mutable state, fixture contention, or cross-test interference, that is a defect.

## Risk-Based Testing Rule

Every feature, flow, and checklist should explicitly consider:

- data loss risk
- silent corruption risk
- concurrency risk
- recovery complexity
- operator confusion risk
- auditability risk
- performance risk
- cross-system contract risk

Higher-risk behavior deserves deeper testing.

## Adversarial Flow Rule

Planned flows should include, where applicable:

- happy path
- invalid input path
- retry path
- pause or interruption path
- recovery path
- conflicting action path
- partial-completion path
- operator diagnosis path
- blocked or impossible state path

## Performance Rule

Performance is part of correctness where the repository depends on repeated inspection, compilation, orchestration, or large state surfaces.

Where performance matters, notes or checklists should define explicit budgets or thresholds.

## Observability And Auditability Rule

A behavior is not fully implemented unless operators can inspect and explain it.

Implementation and tests should account for:

- what durable records are written
- how an operator inspects current state
- how failure causes are inspected
- how lineage and provenance are reconstructed
- how recovery readiness is inspected

## Implementation Expectations

For every meaningful feature, consider explicitly:

1. database changes
2. CLI changes
3. daemon or backend changes
4. website UI changes
5. config or YAML changes
6. prompt changes
7. note updates
8. invariants
9. affected systems
10. canonical verification commands
11. bounded tests
12. E2E tests
13. checklist updates
14. development log updates
15. document consistency tests
16. performance impact
17. observability and auditability impact
18. recovery and concurrency impact

If one of these is not affected, that should be a deliberate conclusion rather than an assumption.

## Stack Decision Maintenance Rule

Do not let primary stack choices remain implicit once the repository has actually chosen them.

When genesis or architecture work selects primary languages, frameworks, persistence layers, test tools, UI stacks, or prompt tooling, record those decisions in the relevant notes, verification commands, and checklists before acting as if they are settled.
