# AGENTS.md

## Purpose

This repository is being built as a spec-driven orchestration system.

Work in this repo must stay aligned with the design notes, authoritative note assets in `notes/`, and authoritative user-documentation assets in `docs/` when those surfaces exist.
Implementation is not allowed to drift away from those artifacts silently.

If coding reveals a limitation, contradiction, missing behavior, needed elaboration, verification gap, runtime mismatch, command inconsistency, or checklist/status mismatch, the relevant note or authoritative note asset in `notes/` must be updated as part of the same change or in an immediately adjacent follow-up change.

This repository does not permit undocumented behavior, undocumented verification steps, undocumented operational assumptions, silent narrowing of behavior to a more convenient implementation path, or completion claims that exceed the actual proving level.

---

## Core Implementation Model

Every feature must be considered across seven required systems.

No feature is complete until its effect on all seven systems has been considered explicitly.

### 1. Database

The database is the durable source of truth for orchestration state and history.

Responsibilities include:

- durable state
- lineage
- run and session state
- prompts and summaries
- quality-gate results
- auditability
- recovery-critical records
- concurrency-sensitive coordination
- restart-safe persistence

Required technology:

- PostgreSQL

### 2. CLI

The CLI is the operational interface for both human operators and AI sessions.

Responsibilities include:

- inspecting current state
- retrieving prompts and context
- recording progress
- recording summaries and failures
- triggering safe runtime actions
- exposing audit and debugging surfaces
- exposing canonical verification commands and diagnostics
- making operational failures inspectable and reproducible

Required technology:

- Python

### 3. Daemon

The daemon is the live orchestration authority.

Responsibilities include:

- validating and applying live mutations
- session binding
- scheduling
- recovery
- pause/resume handling
- authoritative runtime decisions
- safe state transitions
- concurrency control
- idempotent handling where required
- crash-safe and restart-safe behavior

Required technology:

- Python

### 4. YAML

YAML defines declarative structure and policy, not live coordination decisions.

Responsibilities include:

- node definitions
- task definitions
- subtask definitions
- layouts
- validations
- reviews
- testing definitions
- docs definitions
- hooks
- runtime policies where appropriate

All YAML behavior must respect the code/YAML boundary described in `notes/specs/architecture/code_vs_yaml_delineation.md`.

### 5. Prompts

Prompts are first-class implementation assets, not incidental strings.

Responsibilities include:

- decomposition prompts
- execution prompts
- review/testing/docs prompts
- runtime guidance prompts
- error prompts
- missed-step prompts
- pause/recovery/nudge prompts

Prompt behavior must remain aligned with:

- compiled workflow behavior
- CLI surfaces
- validation contracts
- actual daemon behavior
- recovery semantics
- audit expectations

### 6. Website UI

The website UI is the visual operator surface for inspection, navigation, and bounded actions.

Responsibilities include:

- presenting daemon-backed state, lineage, history, and workflow detail clearly
- exposing bounded operator actions without reimplementing orchestration logic in the browser
- preserving stable routes, breadcrumbable navigation, and deep-linkable operator views
- rendering daemon-provided legality, blocked reasons, and confirmations for actions
- keeping browser-visible state consistent with daemon-owned authority and durable records
- providing a browser E2E surface for operator flows that matter in real runtime use

Required technology:

- Node.js
- Vite
- React
- Playwright

### 7. User Documentation

User documentation is the user-facing and operator-facing guidance surface for setup, usage, commands, troubleshooting, and supported workflows.

Responsibilities include:

- onboarding and setup guidance
- user and operator workflow guides
- reference documentation for supported commands, configuration, and interfaces
- runbooks that real operators are expected to follow
- published documentation routes or static documentation artifacts where applicable

Boundary rules:

- `notes/` are governance, planning, specification, and traceability artifacts
- `docs/` are consumer-facing user and operator documentation artifacts
- `notes/scenarios/` is a historical scenario-analysis and migration-pointer source unless a specific file is explicitly re-promoted into the active documentation surface
- YAML `docs` assets define machine-readable documentation outputs; they are not the whole user-documentation system by themselves

---

## System Coverage Rule

Tests must cover all applicable systems touched by a feature, flow, or contract.

It is not acceptable to test only the most convenient or fastest surface when the described behavior spans multiple systems.

If the design says a behavior involves the database, CLI, daemon, website UI, YAML, prompts, or user documentation, the test strategy must explicitly account for each affected system.

Examples of invalid shortcuts include:

- testing only in-memory logic when durable database behavior is part of the feature
- testing only direct Python helpers when the CLI contract is part of the feature
- testing only daemon internals when the user-facing CLI behavior is part of the feature
- testing only daemon or CLI behavior when the user-facing website behavior is part of the feature
- testing only compiled structures when YAML loading or schema behavior is part of the feature
- testing only prompt file existence when prompt/runtime contract behavior is part of the feature

If one of the seven systems is truly not affected, that must be a deliberate conclusion stated in the plan, checklist, note, or review context.

A feature is not considered verified if the tests only prove the convenient fast route while leaving the real described system boundary untested.

---

## Test Progression Rule

Testing must progress in stages.

### Stage 1: Simulated, bounded, or fixture-assisted proof

During initial implementation and code review, simulated, bounded, mocked, or fixture-assisted tests are required and useful.

They should be used to:

- validate logic quickly
- catch regressions early
- refine APIs and behavior
- narrow down bugs while work is still changing rapidly
- support small, fast development tasks

This stage is expected during initial implementation.

### Stage 2: Real end-to-end proof

After the bounded proof exists, every feature must progress to full real end-to-end testing for its intended real behavior.

Real E2E tests must exercise real code paths through the relevant runtime boundaries for the feature, including applicable database, CLI, daemon, YAML, prompt, git, session, provider, or environment behavior.

Simulated or bounded tests do not count as final completion proof for any feature whose behavior is intended to exist in real runtime usage.

There is no feature so small, simple, or low-risk that it is exempt from real E2E coverage.

No feature is complete without full real E2E tests for its intended scope.

If full E2E proof does not yet exist, the feature may be labeled:

- `implemented`
- `in_progress`
- `partial`

It may not be labeled:

- `complete`
- `flow_complete`
- `release_ready`

unless the real E2E layer has been completed for the intended scope.

---

## E2E Coverage Rule

Every feature must be exercisable in real code.

Every feature must map to at least one explicit real E2E test target.

There is no feature too small to require a real E2E test.

Grouped or batched E2E suites are acceptable and preferred where multiple features share one coherent runtime narrative.

One E2E file per feature is not required.

Explicit feature-to-E2E traceability is required.

A feature is not E2E-covered if its strongest test still relies on:

- fake session backends
- in-process daemon bridges as the only proof
- direct DB mutations to skip runtime work
- synthetic prompt, summary, or result injection to bypass the core behavior being claimed
- staged or durable placeholders instead of real git/session/provider behavior where the feature depends on those boundaries

If a feature depends on another feature, both may share one E2E narrative, but both must be explicitly tracked as covered by that E2E suite.

### Live-Run Equivalence Rule

Any test claimed as E2E must test every claimed workflow component as if it were being used in a real live run.

This rule is absolute.

For repository claim purposes, a test is not E2E unless:

- every claimed workflow step happens through the same runtime boundary used in real operation
- every claimed component is exercised through its real role in that workflow
- the test waits for the real system to perform the work being claimed
- the asserted outcome is the result of that real runtime path rather than a shortcut or injected state

There is no acceptable “mostly real” interpretation.

If even one claimed workflow step is skipped, forced, injected, mocked, manually advanced, or satisfied through a lower-layer shortcut, the test must not be treated as E2E coverage for that workflow.

### Forbidden In E2E Rule

The following are forbidden in any test that is claimed as E2E coverage for a workflow:

- fake session backends
- direct DB mutation to force the workflow into a later state
- in-process daemon bridges as the strongest proof
- synthetic prompt, summary, result, or session-pop injection
- direct API completion shortcuts such as `/api/subtasks/complete`
- test-side `subtask start`, `subtask complete`, or `subtask fail` when those actions are supposed to come from live runtime behavior
- test-side `summary register` when the summary is supposed to be produced by the live runtime
- test-side `workflow advance` when the runtime is supposed to advance the workflow itself
- test-side lifecycle transition forcing used to stand in for real runtime progression
- manual child materialization in a test that claims the AI/runtime created descendants itself
- hidden helper behavior that performs the workflow step off-screen and then exposes only the end result
- using a lower-layer proof to stand in for a higher-layer E2E claim

If any of those are present, the workflow is not E2E-covered. The required remediation is to remove the simulation or shortcut and make the test perform the real workflow through the live runtime path. Do not delete, skip, or permanently downgrade the E2E requirement because the test is difficult.

### E2E Naming And Claim Rule

No test, note, checklist, command catalog, plan, review, or assistant response may describe a workflow as E2E-covered, real-E2E-passing, `flow_complete`, or equivalent unless the exact live-run-equivalent workflow has actually been rerun and passed.

The fact that a harness uses a real daemon, real DB, real tmux, or real provider does not make the test E2E if any claimed workflow step is still synthetic.

If a file under `tests/e2e/` is only a bring-up target, partially simulated narrative, or bounded/operator-assisted proof, that status must be stated explicitly and it must be excluded from canonical passing E2E command sets.

Simulation and E2E are opposites in this repository. A simulated workflow may still be useful at a lower layer, but it is never a substitute for the required real E2E proof and it does not reduce the obligation to implement that proof.

---

## Development Operation Logging Rule

All meaningful AI-assisted development work must leave a durable development log under `notes/logs/`.

These logs are for development operations, not product runtime operations.

They exist to make implementation work reconstructible across sessions and to prevent hidden drift between:

- plans
- notes
- code changes
- tests
- checklists
- status claims

### Core rule

No meaningful development task is considered complete unless its development log is current.

A meaningful development task includes:

- setup tasks
- feature tasks
- hardening batches
- E2E implementation tasks
- doc-alignment tasks
- document-schema tasks
- major debugging or remediation tasks
- review or gap-closure passes

Tiny mechanical edits inside an already-logged task do not require separate standalone logs.

### Required logging events

A development log entry is required:

1. Before work starts
2. At major stage transitions
3. At task completion or stop point

Before work starts, the task must log:

- task or plan id
- goal
- affected systems
- plans and notes consulted
- intended verification commands
- key assumptions
- known blockers or risks

At major stage transitions, the task must log when it:

- changes implementation approach
- discovers a contradiction in notes, plans, or code
- discovers a missing dependency
- changes affected systems
- moves from implementation to bounded testing
- moves from bounded testing to E2E work
- becomes blocked, partial, or deferred

At task completion or stop point, the task must log:

- what was actually done
- what changed
- what systems were touched
- what commands and tests were run
- what passed or failed
- resulting status
- remaining gaps
- next required step

### Required log content

Each development log entry must include:

- timestamp or session marker
- task id or batch id
- task title
- status
- affected systems
- summary
- plans and notes consulted
- commands and tests run
- result
- next step

Recommended additional fields:

- files changed
- newly discovered invariants
- newly discovered contradictions
- checklist updates required
- E2E target impacted

### Required status values

Development log status should use explicit values such as:

- `started`
- `in_progress`
- `blocked`
- `changed_plan`
- `bounded_tests_passed`
- `e2e_pending`
- `e2e_passed`
- `partial`
- `deferred`
- `complete`

### Logging scope rule

Logs are required for meaningful work units, not every keystroke.

One log file should correspond to:

- one setup task
- one feature task
- one hardening batch
- one E2E batch
- one doc-update batch
- one document-schema batch
- one major remediation task

Do not create:

- one giant global journal
- one entry per trivial edit
- logs so granular they become unreadable

### Non-substitution rule

Development logs do not replace:

- feature checklists
- note updates
- document-schema updates
- test updates
- commit history
- code comments

They are an additional required artifact.

### Completion rule

A task may not be marked complete unless:

- its log includes a completion entry
- the completion entry records the commands and tests actually run
- the completion entry records the resulting status honestly
- the completion entry records remaining gaps if any exist

If a task stops in a partial or blocked state, that must be logged explicitly before work moves on.

### Folder rule

Development logs must live under `notes/logs/` in a structured hierarchy.

Recommended structure:

- `notes/logs/setup/`
- `notes/logs/features/`
- `notes/logs/hardening/`
- `notes/logs/e2e/`
- `notes/logs/doc_updates/`
- `notes/logs/doc_schemas/`
- `notes/logs/reviews/`

Development-log files are authoritative documents and must follow the repository log schema and consistency tests defined under:

- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`

---

## System Invariants Rule

Every meaningful subsystem must have explicit invariants documented in `notes/` or other approved design artifacts.

Invariants are mandatory implementation assets.

Examples include:

- illegal state transitions that must never occur
- durable records that must always exist before or after specific actions
- lineage relationships that must remain reconstructible
- retry behavior that must not duplicate unsafe side effects
- session/recovery semantics that must survive interruption
- audit records that must be sufficient to explain what happened
- compile/runtime boundaries that must not be crossed by YAML

Tests must defend invariants, not only features.

If a feature is implemented without clarifying the invariants it depends on, the work is incomplete.

---

## Checklist Enforcement Rule

Every meaningful feature must have a checklist entry that tracks implementation and verification status across all affected systems.

Checklists are required implementation assets, not optional project-management aids.

Each feature checklist must track:

- affected systems
- database status
- CLI/API status
- daemon/backend status
- website/frontend status
- YAML/schema status
- prompt status
- user documentation status
- documentation surfaces affected
- notes status
- bounded test status
- E2E test status
- performance/resilience status where applicable
- known limitations
- overall feature status

If a system is not affected, the checklist must mark it explicitly as not applicable rather than omitting it silently.

### Per-system status values

Use one of:

- `not_applicable`
- `planned`
- `in_progress`
- `implemented`
- `verified`
- `partial`
- `blocked`
- `deferred`

### Overall feature status values

Use one of:

- `planned`
- `in_progress`
- `implemented`
- `partial`
- `verified`
- `flow_complete`
- `release_ready`
- `blocked`
- `deferred`

### Checklist consistency rule

Overall feature status must not exceed the weakest required affected-system status.

A feature cannot be marked `verified`, `flow_complete`, or `release_ready` if any required affected system is still:

- `planned`
- `in_progress`
- `partial`
- `blocked`
- `deferred`

E2E status must be tracked explicitly and separately from general test status.

General test completion must not be used as a proxy for E2E completion.

---

## Checklist Maintenance Rule

Checklists are part of the implementation surface.

They must be updated whenever:

- code changes affect a tracked feature
- a feature is found to affect a system that was previously omitted
- test status changes
- E2E status changes
- notes or canonical commands change
- the overall feature status changes
- a limitation becomes known or is resolved

Stale checklists are a correctness problem, not a documentation-polish issue.

No feature may be marked complete if its checklist is stale or missing.

---

## Checklist Granularity Rule

Checklists must be per feature or per tightly related batch of features.

They must not collapse unrelated features into one vague line item.

Grouped batch work is allowed, but each feature in the batch still needs explicit status tracking.

---

## Authoritative Document Rigidity And Consistency Testing Rule

Authoritative documents in this repository are part of the implementation surface.

They must not rely on manual discipline alone for consistency.

Every authoritative document family must have automated tests that enforce the structural, referential, and status-tracking rules that keep the repository from drifting.

### Core rule

If a document family is authoritative, it must have automated consistency tests.

Authoritative document families include, where applicable:

- setup plans
- feature plans
- checklist documents
- flow documents
- flow asset documents
- structured flow inventory documents
- traceability documents
- audit checklist documents
- E2E planning and feature-mapping documents
- document-schema documents
- development logs, if adopted as required artifacts
- other note families that define, track, constrain, or verify implementation behavior

No authoritative document family may remain untested once it becomes part of the required workflow.

### Document-family rule

Tests should be written per authoritative document family, not necessarily one bespoke test per file.

Tests should validate all documents in that family according to the role of the family.

### Required test scope

Document consistency tests should enforce what matters structurally and operationally.

Good enforcement targets include:

- required sections exist
- required headings exist
- required fields exist
- required status values use the allowed vocabulary
- required references or links exist
- required feature, flow, checklist, or E2E entries are present
- file naming conventions
- cross-document consistency
- command-surface consistency
- feature-to-checklist mappings
- feature-to-E2E mappings
- family-specific invariants

Document tests should not generally enforce:

- exact prose wording
- stylistic choices
- incidental phrasing
- large exact-text matches unless the wording itself is a contract

The goal is rigidity of structure and consistency, not rigidity of prose style.

### New family adoption rule

If a new document family becomes authoritative, consistency tests for that family must be added as part of adopting it.

It is not acceptable to create a new required document family and defer its rigidity checks indefinitely.

### Change rule

Whenever an authoritative document changes, the relevant document consistency tests must be run afterward.

If a document change introduces:

- a new required field
- a new status value
- a new section requirement
- a new mapping requirement
- a new command expectation
- a new authoritative document family

then the document tests must be updated in the same change or immediately adjacent follow-up change.

### Completion rule

A documentation change is not complete unless:

- the relevant document consistency tests exist
- those tests were run
- they pass for the changed scope

A new authoritative document family is not fully adopted unless:

- its structural rules are documented
- its family-level consistency tests exist
- those tests are part of the normal proving surface

### Drift rule

Document tests must be designed to catch drift between:

- plans and feature inventory
- feature inventory and checklists
- checklists and status claims
- flow docs and flow tests
- traceability docs and feature or E2E mappings
- command docs and actual canonical commands
- audit/checklist docs and current repo expectations

If an authoritative document can drift silently in a meaningful way, that is a sign the family’s tests are incomplete.

---

## Notes Maintenance Rule

The notes and authoritative note assets in `notes/` are part of the implementation surface.

They must be updated whenever coding reveals:

- a limitation in the current design
- an ambiguity that must be resolved
- a contradiction between notes
- a missing required behavior
- a needed elaboration for implementation clarity
- a boundary change between code and YAML
- a change to prompt expectations
- a change to testing expectations
- a change to performance expectations or budgets
- a change to canonical verification commands
- a change to operational setup or runtime assumptions
- a newly discovered invariant
- a newly discovered failure mode
- a newly discovered recovery or concurrency constraint
- a checklist/status model mismatch
- a document-schema mismatch
- a development-log process mismatch

Do not leave discovered design limitations undocumented.

### User Documentation Maintenance Rule

The authoritative user-documentation assets in `docs/` and any explicitly transitional user/operator documentation surfaces must be updated whenever work changes:

- user-visible behavior
- operator-visible behavior
- setup or onboarding steps
- supported commands, flags, or examples
- configuration or environment requirements presented to users
- troubleshooting or runbook procedures
- recovery behavior that operators are expected to follow
- supported workflows, prerequisites, or limitations

Task plans, feature checklists, and review context must record one of:

- documentation update required
- documentation reviewed with no change required
- documentation not applicable

If the program needs to change or the design needs to be elaborated because of implementation reality, update the relevant note or authoritative note asset or add a new one.

### Relevant User Flow Inventory Rule

Relevant user and operator flows must be tracked through both:

- the canonical narrative flow docs in `flows/*.md`
- the structured relevant-user-flow inventory YAML under `notes/`

When implementation work creates, removes, splits, merges, materially re-scopes, or newly reveals a relevant user/operator flow, the same change or an immediately adjacent follow-up change must update:

- the canonical `flows/*.md` contract if the runtime narrative changed
- the structured flow inventory YAML if relevance, scope, invariants, proof surfaces, or maintenance triggers changed

Do not:

- create a second prose-only canonical flow registry inside `notes/`
- leave a newly relevant flow implicit inside feature notes or checklists
- update a flow checklist or E2E target without reconciling the structured relevant-flow inventory when that flow is affected

---

## Canonical Verification Command Rule

Build, test, validation, migration, flow, audit, and performance commands must be explicitly documented and must not be rediscovered ad hoc during implementation.

Every meaningful setup phase, feature phase, checklist phase, flow, and hardening pass must define its canonical verification commands.

These commands must be:

- written in the relevant plan, checklist, note, or README
- runnable from a clean shell
- consistent with the current repository layout and environment assumptions
- repeated in every authoritative place that claims the work is verified
- updated immediately when the command surface changes

If a contributor has to guess which command proves something, the documentation is incomplete.

If README, notes, plans, checklists, and CI disagree on verification commands, the repository is in an inconsistent state and the inconsistency must be fixed.

Canonical commands must cover, where applicable:

- environment/bootstrap validation
- database migration and schema checks
- unit and bounded tests
- integration tests
- end-to-end tests
- performance checks
- flow-specific verification
- docs/provenance/audit verification if relevant
- document consistency tests if authoritative documents changed

Task plans must include their canonical verification commands explicitly.

---

## Completion Standard

No feature or change is complete without tests.

This rule is absolute.

There is no excuse for skipping tests.

No feature is small enough to be excused from full real E2E proof.

If a change is large enough to matter, it is large enough to deserve tests.

If a change touches behavior, state, contracts, validation, recovery, performance, operability, or user-visible output, it must have test coverage.

A feature is not complete merely because code exists or because a plan/checklist item was updated.

A feature is complete only when all of the following are true:

- the relevant notes are current
- the implementation matches the notes
- invariants are explicit
- the affected systems are explicitly accounted for
- the feature checklist is current
- the required development log entries are current
- the required bounded tests exist
- the required real E2E tests exist
- the required document consistency tests exist for any changed authoritative document families
- the canonical verification commands are documented
- those commands have been run successfully for the intended completion claim
- known limitations are documented explicitly rather than implied

No feature is complete without full real E2E proof for its intended scope.

---

## Completion State Vocabulary

Use the following terms deliberately:

- `implemented`: code/assets exist and bounded proof may exist, but full real E2E proof is not yet complete
- `verified`: the documented canonical verification commands were run successfully for the currently claimed layer and scope
- `partial`: some intended behavior exists, but limitations or missing proving layers remain and are documented explicitly
- `flow_complete`: the intended user or operator flow passes end to end through real code for the declared scope
- `release_ready`: all required bounded tests, real E2E tests, resilience checks, performance checks, notes, commands, and checklists are complete for the intended release scope

Do not describe work as complete if it is only implemented.
Do not describe work as verified if the canonical command was not actually run.
Do not hide partial status behind vague language.

---

## Testing Standard

Tests must be all-encompassing for meaningful behavior.

All tests are expected to be runnable in parallel.

Test isolation is part of correctness, not optional hardening.

A test that passes only when run serially and fails because of parallel execution, shared mutable state, fixture contention, resource collision, or cross-test interference is defective and must be treated as an issue to fix.

External capability gating is a separate concern.

It is acceptable to gate tests on genuinely unavailable requirements such as tmux, git, provider credentials, or similar explicit environment capabilities.

It is not acceptable to normalize serial-only execution because the test or fixture design is not parallel-safe.

That includes:

- normal behavior
- invalid inputs
- boundary cases
- failure paths
- pause paths
- retry paths
- recovery paths
- persistence behavior
- database behavior
- CLI behavior
- daemon behavior
- YAML compilation behavior
- prompt-contract behavior where applicable
- auditability and inspectability expectations
- concurrency behavior where relevant
- idempotency where relevant
- migration compatibility where relevant
- authentication and authorization behavior where relevant

Bounded tests are required during initial implementation and code review.

Full real E2E tests are required before final completion.

Authoritative document-family consistency tests are required wherever document families are part of the implementation surface.

If a feature mutates durable state, the mutation rules must be tested through the real persistence layer where applicable, not only through mocked or in-memory paths.

If a feature depends on ordering, concurrency, retries, recovery behavior, CLI contracts, daemon contracts, YAML compilation, prompt delivery, or other real runtime boundaries, those semantics must be tested explicitly at the proper system boundary.

If a feature is difficult to test, that is a sign the design or implementation should be improved until it becomes testable.

---

## Test Layer Contracts

Tests must be written intentionally at the correct layer.

Parallel-safety applies at every layer.

Unit, integration, performance, resilience, document-consistency, and end-to-end tests should all be able to coexist under parallel execution when their required environment capabilities are present.

Layer choice is not an excuse for shared mutable fixtures or cross-test interference.

### Unit and bounded tests

Use these tests for:

- branch logic
- validation rules
- state-machine legality
- transformation logic
- invariant enforcement
- failure classification
- prompt/rendering contracts
- small persistence rules with narrow scope
- fast review-time feedback during implementation

These tests are required during initial implementation but are not final completion proof for real runtime behavior.

They must still be parallel-safe and must not rely on shared mutable process, filesystem, database, or schema state.

### Integration tests

Use integration tests for:

- database/CLI/daemon boundaries
- migrations
- runtime coordination across modules
- YAML compilation and runtime policy application
- audit/history/provenance persistence
- auth and session boundaries
- flow slices that cross major subsystem boundaries

### End-to-end tests

Use end-to-end tests for:

- real user or operator flows
- real CLI/daemon process boundaries
- real persistence and recovery behavior
- real git/session/runtime coordination where applicable
- full setup-to-outcome flows with no fake skipping of critical boundaries

Critical end-to-end flows must not simulate away the core behavior being claimed.

Simulation and E2E are antonyms in this repository: if a workflow step is simulated, injected, forced, or skipped, the test is not E2E.

For avoidance of doubt:

- an E2E test must execute the workflow as a live run would execute it
- every component named by the workflow must be exercised in that live-run-equivalent path
- if the runtime is supposed to create, advance, summarize, merge, recover, or finalize something, the E2E must wait for the runtime to do exactly that
- if the operator surface is the thing being tested, the E2E may use that real operator surface, but it may not use hidden lower-layer shortcuts to fake the rest of the workflow

An E2E test that mixes real boundaries with synthetic workflow progression is defective and must not be counted as E2E proof.

E2E is the final required proving layer for any feature that is supposed to exist in real runtime behavior.

Do not remove, skip, or waive E2E coverage because implementation is difficult. The correct response to a defective simulated E2E is to make the test run the real workflow.

Real-runtime resource needs such as tmux, git, ports, workspaces, tokens, and databases must be isolated so eligible E2E tests can run concurrently.

### Document consistency tests

Use document consistency tests for:

- required document structure
- status vocabulary enforcement
- feature, checklist, and E2E mapping integrity
- command reference consistency
- required section and field presence
- document-family-specific invariants

Document consistency tests are mandatory for authoritative document families and must be rerun after those documents change.

These tests should also remain parallel-safe; document-only verification is not exempt from the repository isolation rule.

### Performance tests

Use performance tests for:

- repeated inspection paths
- workflow compilation cost
- daemon scheduling overhead
- database query efficiency
- startup/recovery overhead
- high-frequency runtime lookups
- any path explicitly designated performance-sensitive

### Resilience tests

Use resilience tests for:

- interruption
- restart
- retry after partial completion
- duplicate request handling
- stale session recovery
- durable audit/recovery correctness after failure

Do not duplicate the same assertion at every layer without reason.
Prefer the lowest layer that can prove the behavior clearly.
Use higher-layer tests when the boundary itself is what matters.

---

## Risk-Based Testing Rule

Exhaustiveness is required for meaningful behavior, but effort must be directed by risk.

Every feature, flow, and checklist should explicitly consider:

- data loss risk
- silent corruption risk
- concurrency risk
- recovery complexity
- operator confusion risk
- auditability risk
- performance risk
- cross-system contract risk

Higher-risk behavior deserves deeper and more adversarial testing.

Do not satisfy the testing rule with large quantities of low-value tests.

The standard is not test count.
The standard is defended behavior.

---

## User Flow And Adversarial Flow Rule

Planned flows must include both expected user journeys and adversarial or interruption journeys.

Required flow categories include, where applicable:

- happy path
- abandonment path
- invalid input path
- retry path
- pause/resume path
- recovery-after-interruption path
- conflicting/concurrent action path
- partial-completion path
- operator inspection/diagnosis path
- impossible or blocked state path

A system is not sufficiently tested if it only works on its intended path.

---

## Performance Requirement

Performance must be considered during implementation and testing.

Performance is not optional polish.

It is part of correctness for this system because the project depends on:

- frequent state inspection
- workflow compilation
- orchestration loops
- database-backed coordination
- potentially large prompt/history/state surfaces

Performance-oriented testing must be added where appropriate, including:

- query efficiency
- workflow compilation cost
- CLI responsiveness
- daemon scheduling overhead
- recovery-path overhead
- repeated inspection-path cost

Where performance matters, notes or checklists should define explicit budgets or thresholds.

If a path is called performance-sensitive, the intended threshold must be documented.

Changes that introduce obviously avoidable inefficiency are not complete.

---

## Observability And Auditability Rule

A behavior is not fully implemented unless operators can inspect and explain it.

Implementation and tests should explicitly account for:

- what durable records are written
- how an operator inspects state
- how an operator inspects failure cause
- how an operator inspects lineage and provenance
- how an operator inspects summaries, prompts, and attempts
- how an operator inspects recovery readiness
- whether audit history is sufficient to reconstruct what happened

If something can happen but cannot be diagnosed through the intended surfaces, the feature is incomplete.

---

## Implementation Expectations

For every feature, implementation work should explicitly account for:

1. database changes
2. CLI changes
3. daemon changes
4. website UI changes
5. YAML changes
6. prompt changes
7. user-documentation changes
8. note updates
9. invariants
10. affected systems
11. canonical verification commands
12. documentation verification commands
13. bounded tests
14. E2E tests
15. checklist updates
16. development log updates
17. document consistency tests
18. performance impact
19. observability and auditability impact
20. recovery and concurrency impact

If one of those categories is truly not affected, that should be a deliberate conclusion, not an assumption.

---

## Stack Requirements

The required implementation stack for this repository is:

- PostgreSQL for the database
- Python for the daemon
- Python for the CLI
- Node.js + Vite + React for the website UI
- FastAPI + Uvicorn for the daemon/API server by default
- SQLAlchemy + Alembic for ORM and migrations by default
- Pydantic for request/response/config models by default
- pytest as the default testing framework
- Playwright as the default browser E2E framework

Do not introduce an alternative primary database or alternative primary daemon/CLI language without first updating the notes and explicitly revisiting the architectural decision.
Do not swap out the default daemon/API framework stack without first updating the notes and explicitly revisiting the architectural decision.
Do not swap out the default ORM, migration, model, or testing stack without first updating the notes and explicitly revisiting the architectural decision.

### Default runtime posture

- FastAPI may remain async at the request layer
- synchronous PostgreSQL access is acceptable if used deliberately behind the request layer
- if synchronous DB access is used behind async FastAPI handlers, concurrency and latency behavior must be tested explicitly

### Default daemon auth posture

The daemon API should use bearer-token authentication backed by a local magic-cookie file.

Default expectation:

- daemon startup creates or loads a local auth token
- the token is written to a user-accessible local path
- CLI reads the token and sends it as a bearer token
- daemon APIs require that token unless explicitly documented otherwise

If this auth model changes, the notes and plans must be updated.

---

## Practical Rule For Contributors

When implementing or revising a feature, ask:

1. What changes in PostgreSQL?
2. What changes in the Python CLI?
3. What changes in the Python daemon?
4. What changes in the website UI?
5. What YAML definitions or policies change?
6. What prompts change?
7. What user documentation must change?
8. What notes must be updated?
9. What invariants are being introduced, changed, or defended?
10. Which of the seven systems are actually affected?
11. What are the canonical verification commands for this work?
12. What documentation verification commands apply?
13. What bounded tests prove the behavior during implementation?
14. What real E2E test proves the intended runtime behavior?
15. What checklist entries and statuses must be updated?
14. What development log entries must be written?
15. What authoritative document families changed, and which document consistency tests must run?
16. What performance risks must be measured or guarded?
17. What recovery, idempotency, or concurrency semantics must be proven?
18. What operator/audit surfaces must exist to inspect the result?

If those questions are not answered, the feature is not done.

---

## Doctrine For Plans, Checklists, And Flows

Plans, checklists, and flows are implementation assets, not informal brainstorming notes.

## Mandatory Task Plan Rule

Every meaningful task must have a written task plan before execution begins.

Every code change must be associated with a task plan stored under:

- `plan/tasks/<task_name>.md`

Do not execute a code change without an associated verified and tested task plan.

For this rule:

- a meaningful task includes feature work, bug fixes, hardening work, refactors that affect behavior or contracts, doc-alignment work tied to implementation claims, and meaningful test-surface changes
- tiny mechanical edits may be grouped into an already-open task plan, but they may not be performed without plan coverage
- the governing task plan must be current before implementation continues if task scope changes materially

Task plans are authoritative documents.

They must:

- follow the repository standard plan schema
- pass the relevant document consistency tests
- record the canonical verification commands for the task
- record the intended bounded proof for the task
- record the intended real E2E target or explicitly state why real E2E is not yet in scope

Every code change must point back to its governing task plan in at least one adjacent implementation artifact such as:

- the development log
- a checklist update
- an implementation decision note
- review context

Do not:

- start implementation and write the task plan afterward
- rely on an implied or unwritten task plan
- claim a task was planned if the plan file was not validated under the document-schema tests
- continue implementing after the task has outgrown its written plan without updating that plan first

## Standard Plan Schema Rule

The repository standard richer plan schema is the formal schema used by feature plans and task plans.

The standard richer plan schema requires:

- `## Goal`
- `## Rationale`
- `## Related Features`
- `## Required Notes`
- `## Scope`

The `## Rationale` section must include:

- `- Rationale: ...`
- `- Reason for existence: ...`

The `## Related Features` section must include the guidance line:

- `Read these feature plans for implementation context and interaction boundaries:`

The `## Required Notes` section must include the guidance line:

- `Read these note files before implementing or revising this phase:`

The `## Scope` section must explicitly address:

- Database
- CLI
- Daemon
- Website
- YAML
- Prompts
- Tests
- Performance
- Notes

Task plans must use the standard richer plan schema and additionally include:

- `## Verification`
- `## Exit Criteria`

Each meaningful plan, checklist, or flow should state:

- scope
- rationale
- related notes/specs/features
- affected systems
- invariants affected
- completion criteria
- canonical verification commands
- known limitations or non-goals
- expected test layers
- checklist status model
- document rigidity rules if the family is authoritative
- performance expectations if applicable

If a flow is marked partial, the missing behavior must be stated plainly.
If a flow is marked verified, the exact proving command must be recorded.
If a feature is intentionally deferred, that deferral must be explicit.

---

## Release And Hardening Rule

A release or major hardening pass is not complete until:

- critical flows pass with canonical commands
- known high-risk invariants are defended by tests
- affected systems have all been exercised where applicable
- every included feature has real E2E coverage or is explicitly marked partial/deferred
- authoritative document families touched by the release have passing consistency tests
- partial areas are documented explicitly
- recovery behavior has been exercised where relevant
- performance-sensitive paths have been checked against expectations
- build/test/run commands are consistent across README, notes, plans, checklists, and CI
- no known design limitation discovered during hardening remains undocumented

---

## Prohibited Behaviors

Do not:

- silently diverge from `notes/`
- execute a code change without an associated verified and tested task plan
- claim verification without running the documented command
- rely on ad hoc shell knowledge that is not written down
- test only the convenient fast route when the real feature spans multiple systems
- replace database-backed behavior tests with purely in-memory proof when durability is part of the contract
- treat bounded or simulated tests as final completion proof
- mark a feature complete before real E2E coverage exists for its intended scope
- leave a feature without an explicit E2E target
- treat authoritative documents as untested prose
- add a new required document family without adding its consistency tests
- change required document structure without updating tests
- treat artifact existence as proof of completion
- hide partial implementation behind vague wording
- add tests that only satisfy form while leaving risk unaddressed
- skip note updates when implementation reality changes the design
- leave canonical commands inconsistent across repository surfaces
- leave checklists stale while claiming feature progress or completion
- leave development logs stale while claiming task progress or completion
