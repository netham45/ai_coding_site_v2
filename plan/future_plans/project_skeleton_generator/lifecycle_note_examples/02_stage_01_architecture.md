# Stage 01: Architecture

## Purpose

Architecture converts the idea into a concrete system model.

This stage defines:

- system boundaries
- durable state
- main runtime loops
- code versus config boundaries
- verification command surfaces
- initial testing posture

## Stage Sub-Steps

### `architecture.define_boundaries`

Why it exists:

- prevent system responsibilities from drifting into code without notes

Required artifacts:

- architecture overview
- system-boundary notes

Acceptance criteria:

- the durable authority boundary is described
- major systems have explicit ownership or responsibility statements
- contributors can tell where core decisions belong

Proof required:

- artifact existence check

Blocked claims:

- setup can proceed safely

Advance when:

- the major system boundaries are explicit enough that setup does not need to guess them

### `architecture.define_state_and_runtime_model`

Why it exists:

- make persistence, runtime, and recovery expectations concrete early

Required artifacts:

- durable-state note if persistence exists
- runtime model note

Acceptance criteria:

- the durable source of truth is named
- core runtime loops or authorities are described
- recovery, audit, or concurrency-sensitive assumptions are at least sketched

Proof required:

- artifact existence check

Blocked claims:

- runtime expectations are settled

Advance when:

- the repository has a written starting runtime model instead of only intuition

### `architecture.define_code_config_boundary`

Why it exists:

- stop declarative and imperative responsibilities from blurring immediately

Required artifacts:

- code-vs-config or code-vs-YAML delineation note

Acceptance criteria:

- the repo explains what belongs in code
- the repo explains what belongs in config or YAML
- known gray areas are called out explicitly

Proof required:

- artifact existence check

Blocked claims:

- config surfaces are implementation-ready

Advance when:

- contributors can tell where new behavior should live without inventing the rule from memory

### `architecture.define_real_commands`

Why it exists:

- prevent later stages from inheriting fake proof commands

Required artifacts:

- initial verification command catalog

Acceptance criteria:

- bootstrap, bounded-test, and future E2E command surfaces are named
- commands intended for immediate use are real, not placeholder prose
- command docs say honestly what is still future work

Proof required:

- artifact existence check
- manual command review for placeholder leakage

Blocked claims:

- bounded verification is ready

Advance when:

- setup can inherit real commands for the surfaces it is expected to prove

### `architecture.advance_operational_state`

Why it exists:

- make the handoff to setup explicit and durable

Required artifacts:

- operational-state checklist update

Acceptance criteria:

- the current stage is still recorded honestly
- setup entry expectations are written down
- blocked stronger claims remain explicit

Proof required:

- artifact existence check

Blocked claims:

- setup is active without a stage record

Advance when:

- the operational-state checklist can honestly record architecture as sufficient for setup handoff

## What This Stage Should Produce

Minimum expected artifacts:

- architecture notes
- one note per critical boundary
- initial command catalog
- setup plans
- first checklist structure
- operational-state advancement criteria for setup

## Recommended Files

- `notes/specs/architecture/authority_and_api_model.md`
- `notes/specs/architecture/code_vs_config_delineation.md`
- `notes/specs/database/database_schema.md`
- `notes/specs/runtime/runtime_model.md`
- `notes/specs/cli/cli_surface.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `plan/setup/00_project_bootstrap.md`
- `plan/checklists/00_project_operational_state.md`

## Questions This Stage Must Answer

- What is the durable source of truth?
- What is decided in code versus in config?
- What operations require audit history?
- What commands prove bootstrap, tests, and E2E?
- What failure, recovery, or concurrency semantics matter from day one?
- Has the operational-state checklist recorded architecture as the current active gate correctly?

## AI Instruction

If the repository is in architecture stage, AI contributors should:

- add notes before or with implementation changes
- preserve explicit system boundaries
- surface contradictions instead of silently picking one side
- make command expectations real enough for the next stage rather than leaving them as fake placeholders
- avoid burying architecture decisions in code only

Suggested `AGENTS.md` line:

> During architecture work, update the relevant notes when implementation reveals a missing boundary, invariant, command, or recovery rule. Do not leave architectural decisions implicit in code.

## Entry Conditions

- Genesis artifacts exist.
- The project mission and major systems are already named.
- The next need is system definition rather than code execution.

## Required Artifacts

- architecture overview
- system-boundary notes
- durable-state note if persistence exists
- verification command catalog draft
- first setup-plan set
- operational-state checklist updates

## Required Verification Surface

This stage should prove:

- the architecture docs exist
- the command catalog exists
- setup plans point to the intended proving commands

Real product E2E proof is usually still not expected here.

## Common Failure Modes

- Blurring code and config responsibilities.
- Naming primary systems but not assigning responsibilities.
- Forgetting to define canonical commands.
- Making durable state decisions without documenting audit or recovery expectations.
- Treating placeholder commands as sufficient architecture proof for setup handoff.

## Exit Conditions

Architecture is complete enough to exit when:

- the major boundaries are explicit
- the stack direction is documented
- the initial proving commands are documented
- the operational-state checklist can honestly advance toward setup
- setup work can begin without guessing the intended system model

## Example Deliverable

Example command-catalog snippet:

```md
# Verification Command Catalog

- Bootstrap validation: `make bootstrap-check`
- Unit tests: `pytest tests/unit`
- Integration tests: `pytest tests/integration`
- E2E tests: `pytest tests/e2e`
```
