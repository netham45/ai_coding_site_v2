# AGENTS.md

## Purpose

This repository is being built as a spec-driven orchestration system.

Work in this repo must stay aligned with the design notes in `notes/`.
Implementation is not allowed to drift away from the notes silently.

If coding reveals a limitation, contradiction, missing behavior, or a needed elaboration, the relevant note in `notes/` must be updated as part of the same change or immediately adjacent follow-up work.

---

## Core Implementation Model

Every feature must be considered across five required systems.

No feature is complete until its effect on all five systems has been considered explicitly.

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

All YAML behavior must respect the code/YAML boundary described in `notes/code_vs_yaml_delineation.md`.

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

---

## Notes Maintenance Rule

The notes in `notes/` are part of the implementation surface.

They must be updated whenever coding reveals:

- a limitation in the current design
- an ambiguity that must be resolved
- a contradiction between notes
- a missing required behavior
- a needed elaboration for implementation clarity
- a boundary change between code and YAML
- a change to prompt expectations
- a change to testing expectations

Do not leave discovered design limitations undocumented.

If the program needs to change or the design needs to be elaborated because of implementation reality, update the relevant note or add a new note.

---

## Completion Standard

No feature or change is complete without tests.

This rule is absolute.

There is no excuse for skipping tests.

If a change is large enough to matter, it is large enough to deserve tests.

If a change touches behavior, state, contracts, validation, recovery, performance, or user-visible output, it must have test coverage.

---

## Testing Standard

Tests must be all-encompassing.

A feature is not implemented until tests cover every meaningful aspect of it.

That includes:

- normal behavior
- invalid inputs
- boundary cases
- failure paths
- pause paths
- retry paths
- recovery paths
- persistence behavior
- CLI behavior
- daemon behavior
- YAML compilation behavior
- prompt-contract behavior where applicable
- auditability and inspectability expectations

Unit tests are required for every feature.

If a feature has multiple internal branches, all branches must be tested.

If a feature mutates durable state, the mutation rules must be tested.

If a feature depends on ordering, concurrency, retries, or recovery behavior, those semantics must be tested explicitly.

If a feature is difficult to test, that is a sign the design or implementation should be improved until it becomes testable.

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

Changes that introduce obviously avoidable inefficiency are not complete.

---

## Implementation Expectations

For every feature, implementation work should explicitly account for:

1. database changes
2. CLI changes
3. daemon changes
4. YAML changes
5. prompt changes
6. note updates
7. exhaustive tests
8. performance impact

If one of those categories is truly not affected, that should be a deliberate conclusion, not an assumption.

---

## Stack Requirements

The required implementation stack for this repository is:

- PostgreSQL for the database
- Python for the daemon
- Python for the CLI
- FastAPI + Uvicorn for the daemon/API server by default
- SQLAlchemy + Alembic for ORM and migrations by default
- Pydantic for request/response/config models by default
- pytest as the default testing framework

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

When implementing a feature, ask:

1. What changes in PostgreSQL?
2. What changes in the Python CLI?
3. What changes in the Python daemon?
4. What YAML definitions or policies change?
5. What prompts change?
6. What notes must be updated?
7. What tests prove every aspect of this feature?
8. What performance risks must be measured or guarded?

If those questions are not answered, the feature is not done.
