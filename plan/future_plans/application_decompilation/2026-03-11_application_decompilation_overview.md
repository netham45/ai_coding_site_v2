# Application Decompilation Overview

## Purpose

Preserve a future idea for an "application to prompts" decompilation workflow.

The rough ambition is:

- take an existing application
- inspect and execute it
- derive a defensible behavior map
- turn that behavior map into tests, notes, prompts, and planning assets
- emit a reconstruction backlog made of epics, phases, plans, and tasks

This is not an implementation plan.

It is a working note for a speculative follow-on concept.

## Position In The Roadmap

If this idea ever becomes real work, it should come after the future directions already captured in:

- `plan/future_plans/workflow_overhaul/`
- `plan/future_plans/project_skeleton_generator/`

Reason:

- `workflow_overhaul` is the prerequisite for richer profile-aware decomposition, role coverage, and tier-specific closure obligations
- `project_skeleton_generator` is the prerequisite for emitting a rebuild target that has a sane operational doctrine instead of a pile of code-generation output

This decompilation idea is effectively:

- workflow-overhaul profiles applied to reverse-engineering
- plus project-skeleton generation applied to the rebuilt target

## Core Idea

The future workflow would accept an existing application as input and produce two major outputs:

1. A decompilation dossier
2. A reconstruction plan set

The decompilation dossier would likely include:

- source inventory
- runtime entrypoint inventory
- dependency and service map
- externally visible behavior map
- inferred architecture notes
- identified invariants
- unresolved ambiguity list
- risk map
- provenance links from observations to generated conclusions

The reconstruction plan set would likely include:

- top-level epics
- phase decomposition
- plan-level execution packets
- task-level implementation, docs, verification, and remediation work
- required bounded-test and real-E2E proving targets

The conceptual output is not "copy the source code."

The conceptual output is "produce a plan-and-proof system that can recreate the application intentionally."

## Why This Is Interesting

This is one of the stronger possible demonstrations of the repository's broader thesis:

- prompts can be treated as implementation assets
- plans can be generated from real evidence rather than hand-written guesses
- tests can anchor reconstruction work
- decomposition can be auditable instead of magical

If it worked well enough, it would create a path from:

- running software

to:

- observable behavior
- structured test coverage
- architecture recovery
- rebuild planning

## Why This Is Very Exploratory

This idea has several hard problems that should be made explicit early.

### "100% Coverage" Is Not Something The Note Can Promise

The original idea wants unit, integration, and E2E tests with 100% coverage.

That should be treated as an aspiration, not as a claimable output of the future workflow by default.

At minimum, any serious future version would need to separate:

- line or branch coverage
- interface and behavior coverage
- environment and configuration coverage
- failure and recovery-path coverage
- operator-inspection coverage

A decompilation pipeline might be able to produce:

- a measured coverage baseline
- missing-coverage inventories
- generated candidate tests
- parity-check suites

It should not silently claim full coverage just because many tests were emitted.

### Observed Behavior And Inferred Intent Are Different

An existing application contains:

- observable behavior
- implementation artifacts
- accidental quirks
- historical debt
- missing tests
- undocumented assumptions

A future decompilation workflow must distinguish:

- what was directly observed
- what was inferred from static analysis
- what was inferred from runtime probing
- what was guessed and still requires human confirmation

Otherwise the generated rebuild plan would pretend to know design intent when it only knows symptoms.

### Legal And Product Boundaries Matter

This future concept should be framed as:

- analysis and reconstruction planning for applications you are allowed to inspect and reproduce

not as:

- a generic code-cloning shortcut

The future note should stay clear that provenance, attribution, and permission boundaries would matter.

## Rough End-To-End Flow

The current best rough shape is a staged pipeline.

### Stage 0: Ingest And Safety Framing

Input assumptions:

- local repository or checked-out application source
- runnable environment or at least inspectable build metadata
- explicit statement of what the operator is allowed to analyze and reproduce

Likely outputs:

- source root registration
- runtime capability check
- language and framework inventory
- initial risk flags
- decompilation session record

### Stage 1: Source And Runtime Discovery

Goal:

- understand what exists before generating any reconstruction work

Likely activities:

- identify entrypoints, services, scripts, routes, jobs, and background workers
- inventory databases, queues, APIs, and external integrations
- map tests that already exist
- collect dependency manifests and build commands
- detect UI surfaces, CLI surfaces, and daemon or API surfaces

Likely outputs:

- system inventory
- runtime topology draft
- executable command catalog
- initial component graph

### Stage 2: Behavioral Capture And Test Extraction

Goal:

- convert observable behavior into structured proving targets

Likely activities:

- run existing tests and coverage tooling
- probe key user and operator flows
- classify flows into unit, integration, and E2E candidates
- identify gaps between existing tests and observed behavior
- generate candidate tests with provenance back to observed behavior

Likely outputs:

- coverage baseline
- test-gap matrix
- generated test candidates
- confidence scores on each proposed proving layer

This is where the "100% coverage" ambition would need the most discipline.

The system should probably emit:

- what is proven
- what is partially proven
- what is still ambiguous

instead of flattening everything into one coverage percentage.

### Stage 3: Architecture Recovery

Goal:

- infer how the application is organized well enough to rebuild it intentionally

Likely activities:

- infer bounded contexts, modules, services, and data ownership
- identify durable-state boundaries
- identify orchestration loops and background processes
- recover configuration, deployment, and environment assumptions
- recover prompts or instruction assets if the source application is itself AI-driven

Likely outputs:

- architecture notes
- invariants draft
- dependency graph
- recovery and failure-path inventory
- unresolved contradiction list

### Stage 4: Reconstruction Scaffold Generation

Goal:

- create the target shape of a rebuilt project before deep implementation planning

This stage is where the concept should likely lean on the future `project_skeleton_generator` direction.

Likely outputs:

- proposed repository skeleton
- initial `AGENTS.md`
- note families and checklist families
- canonical command placeholders
- starter workflow-profile suggestions for the rebuild effort

### Stage 5: Workflow Synthesis

Goal:

- turn the recovered architecture and proof obligations into executable planning assets

This stage is where the concept should likely lean on the future `workflow_overhaul` direction.

Likely outputs:

- epic profiles for major product areas
- phase breakdown for discovery, implementation, docs, E2E, review, and remediation
- plan decomposition for executable work packets
- task decomposition with explicit note, checklist, log, and verification obligations

Example high-level epics the system might emit:

- platform and runtime skeleton
- persistent data model recreation
- API and backend behavior recreation
- frontend or UI recreation
- integration and provider recreation
- docs and operator-surface recreation
- real parity-verification and hardening

### Stage 6: Rebuild And Parity Validation

Goal:

- prove the reconstructed application matches the intended observed behavior closely enough for the declared scope

Likely activities:

- execute generated bounded tests
- execute generated real E2E suites
- compare source-app vs rebuilt-app outputs where possible
- record parity failures and regenerate plans

Likely outputs:

- parity report
- mismatch inventory
- remediation work
- scope-qualified completion or partial status

## What The Five-System Model Would Probably Look Like

If this ever becomes real implementation work, it should still be forced through the repository's five-system model.

### Database

Likely future responsibilities:

- decompilation sessions
- source artifact lineage
- observed-command history
- coverage snapshots
- generated test provenance
- architecture inference records
- rebuild-parity results
- ambiguity and confidence tracking

### CLI

Likely future responsibilities:

- start decompilation
- inspect discovery findings
- inspect generated tests and confidence
- inspect inferred architecture and open ambiguities
- export reconstruction plans
- run or rerun parity checks

### Daemon

Likely future responsibilities:

- orchestrate long-running analysis stages
- enforce stage ordering and human review gates
- coordinate retries and resumability
- persist auditable lineage between source observations and emitted planning assets

### YAML

Likely future responsibilities:

- declarative workflow profiles for discovery, extraction, reconstruction, and parity
- layout definitions for decompilation dossiers and reconstruction epics
- review policy declarations for ambiguity or low-confidence stages

### Prompts

Likely future responsibilities:

- source-inventory prompts
- architecture-recovery prompts
- test-generation prompts
- parity-analysis prompts
- reconstruction planning prompts
- ambiguity and confidence-report prompts

## Likely Workflow Profiles

If this concept ever uses the profile-aware model from `workflow_overhaul`, plausible draft profiles would include:

- `epic.decompilation`
- `phase.discovery`
- `phase.behavior_capture`
- `phase.architecture_recovery`
- `phase.reconstruction_scaffold`
- `phase.rebuild`
- `phase.parity`
- `plan.analysis`
- `plan.test_extraction`
- `plan.rebuild_execution`
- `plan.parity_verification`
- `task.inventory`
- `task.runtime_probe`
- `task.test_authoring`
- `task.architecture_note_authoring`
- `task.docs`
- `task.e2e`
- `task.remediation`

Those names are only placeholders.

The main point is that this idea would need workflow roles beyond the repository's current simpler default ladder.

## Invariants And Guardrails Worth Preserving

Any later serious version should probably preserve the following rules.

- Never claim "100% coverage" unless the actual proving surface and gap registry justify that exact statement.
- Never collapse observed facts and inferred architecture into one undifferentiated summary.
- Every generated test should retain provenance back to the observation, file, runtime trace, or existing behavior that justified it.
- Every generated plan should retain provenance back to the recovered architecture or explicit ambiguity it addresses.
- The rebuild target should be allowed to diverge intentionally when the source app contains bugs or debt, but those divergences must be explicit.
- Human review gates are required for low-confidence inference, licensing concerns, security-sensitive flows, and parity mismatches.

## Risks

Major risks that make this a future-plan-only idea for now:

- static analysis may be shallow for dynamic or reflection-heavy systems
- runtime probing may be expensive, flaky, or unsafe
- generated tests may overfit current implementation quirks
- coverage numbers may create false confidence
- inferred architecture may be cleaner or messier than the original product intent
- source applications may span technologies this repository cannot model yet
- parity proof may require infrastructure the future system cannot reproduce automatically

## Minimum Sensible Future Scope

If this idea were ever promoted, the smallest sensible real scope would probably be narrow.

Example:

- one local application
- one language stack
- one main runtime surface
- one bounded parity target
- explicit human review between each major stage

That is a much safer first target than "clone any application."

## Rough Summary

The future task would likely look like this:

- ingest an existing application and capture what can be observed safely
- convert those observations into a coverage baseline and structured test-gap inventory
- recover architecture and invariants with explicit confidence levels
- generate a rebuild skeleton and workflow-profile-aware planning tree
- execute reconstruction and compare the rebuilt app against the original for the declared scope

In short, this is not really "copy an app."

It is "decompile an app into evidence, prompts, tests, and reconstruction plans."
