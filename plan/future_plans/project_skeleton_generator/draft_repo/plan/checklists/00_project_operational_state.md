# Project Operational State

## Goal

Track the repository's current operational maturity honestly.

Use this checklist to:

- record the current lifecycle stage
- record which sub-steps are complete
- record what stronger claims are blocked
- record what must pass before the repository advances

## Current State

- Active stage: `genesis`
- Current maturity status: `genesis_in_progress`
- Next target stage: `architecture_defined`
- Stronger claims currently blocked: `verified`, `flow_complete`, `release_ready`
- Governing references:
  - `notes/lifecycle/00_project_lifecycle_overview.md`
  - `notes/lifecycle/01_stage_00_genesis.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`

## State Table

| State | Status | Current stage? | Acceptance summary | Proof summary | Blocked stronger claims | Advance when |
| --- | --- | --- | --- | --- | --- | --- |
| `genesis` | in_progress | yes | Mission, systems, initial invariants, and bootstrap governance are being established. | Artifact creation and early document checks are expected first. | `verified`, `flow_complete`, `release_ready` | Architecture inputs are explicit and governed. |
| `architecture_defined` | planned | no | Boundaries, durable state, code-vs-config lines, and command surfaces are documented. | Architecture notes and command catalog exist. | `flow_complete`, `release_ready` | Setup can begin without guessing system boundaries. |
| `setup_bootstrapped` | planned | no | Scaffold, starter tests, governing artifacts, and bounded proof exist. | Bounded commands pass from a clean shell. | `flow_complete`, `release_ready` | Feature work can proceed without ad hoc process invention. |
| `feature_delivery_ready` | planned | no | Task plans, logs, checklists, and note maintenance operate reliably for feature work. | A real feature slice is governed and bounded-tested. | `flow_complete`, `release_ready` | Features can ship under consistent doctrine. |
| `bounded_verified` | blocked | no | Bounded proof discipline exists across the active scope. | Current bounded commands and doc checks pass. | `flow_complete`, `release_ready` | Active features are honestly proven at the bounded layer. |
| `e2e_ready` | blocked | no | Real E2E targets and mapping exist for intended runtime behavior. | E2E execution policy and traceability docs agree. | `release_ready` | The next runtime narrative is concrete enough to test. |
| `flow_complete` | blocked | no | A declared runtime narrative passes end to end for the stated scope. | The real E2E command has passed. | N/A | A named real flow is proven and documented. |
| `release_ready` | blocked | no | Release-scope proof, readiness docs, and risk treatment are complete. | Required bounded, E2E, resilience, and audit surfaces pass. | N/A | The declared release scope is honestly proven. |

## Active Stage Sub-Steps

### `genesis.capture_mission`

- Status: `planned`
- Required artifacts:
  - `notes/explorations/original_concept.md`
- Advance when:
  - the repo mission is durable and specific

### `genesis.define_system_inventory`

- Status: `planned`
- Required artifacts:
  - `notes/catalogs/inventory/system_inventory.md`
- Advance when:
  - the primary systems are explicit

### `genesis.record_invariants_and_unknowns`

- Status: `planned`
- Required artifacts:
  - `notes/explorations/initial_risks_and_unknowns.md`
  - `notes/specs/architecture/authority_and_api_model.md`
- Advance when:
  - first invariants and unknowns are written down

### `genesis.record_stack_direction`

- Status: `planned`
- Required artifacts:
  - `notes/specs/architecture/stack_decision_record.md`
- Advance when:
  - stack choices are either explicitly undecided or explicitly proposed without being implied silently

### `genesis.seed_bootstrap_governance`

- Status: `planned`
- Required artifacts:
  - `plan/tasks/2026-03-12_project_bootstrap.md`
  - `notes/logs/setup/2026-03-12_project_bootstrap.md`
- Advance when:
  - the first work is plan-governed and logged

### `genesis.initialize_operational_state`

- Status: `complete`
- Required artifacts:
  - this file
- Advance when:
  - the repo has a durable stage rollup surface
