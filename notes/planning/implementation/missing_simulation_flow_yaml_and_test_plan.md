# Missing Simulation Flow YAML And Test Plan

## Goal

Add explicit YAML flow assets under `flows/` for every simulation-proposed flow that still lacks a dedicated flow document, and add a pytest-backed contract for each one.

This plan is intentionally phased. Each phase should:

1. author the flow YAML
2. add or extend the flow-contract test
3. run the targeted pytest slice
4. document any missing runtime or note gaps exposed by that test before moving on

## Source inventory

This plan is based on the deduplicated gap list in:

- `notes/catalogs/traceability/simulation_flow_union_inventory.md`

## Missing flow YAML files to add

These are the concrete flow YAML assets that should be created in `flows/`.

1. `14_project_bootstrap_and_yaml_onboarding_flow.yaml`
   - Source simulation: `simulations/12_project_bootstrap_flow.md`

2. `15_epic_default_workflow_blueprint_flow.yaml`
   - Source simulation: `simulations/08_epic_default_flow.md`

3. `16_phase_default_workflow_blueprint_flow.yaml`
   - Source simulation: `simulations/09_phase_default_flow.md`

4. `17_plan_default_workflow_blueprint_flow.yaml`
   - Source simulation: `simulations/10_plan_default_flow.md`

5. `18_task_default_workflow_blueprint_flow.yaml`
   - Source simulation: `simulations/11_task_default_flow.md`

6. `19_hook_expansion_compile_stage_flow.yaml`
   - Source simulation: `simulations/14_hook_expansion_flow.md`

7. `20_compile_failure_and_reattempt_flow.yaml`
   - Source simulations:
     - `simulations/13_compile_failure_flow.md`
     - `simulations2/05_compile_failure_and_reattempt_flow.md`

8. `21_child_session_round_trip_and_mergeback_flow.yaml`
   - Source simulations:
     - `simulations/17_child_session_mergeback_flow.md`
     - `simulations2/04_child_session_round_trip_flow.md`

9. `22_dependency_blocked_sibling_wait_flow.yaml`
   - Source simulation: `simulations2/01_dependency_blocked_sibling_flow.md`

## Expected matching tests

The target shape is one executable contract per new flow, added to the current flow suite or split into a new YAML-backed suite if that becomes cleaner.

Minimum expected test coverage:

1. `test_flow_contract_cases[14]`
2. `test_flow_contract_cases[15]`
3. `test_flow_contract_cases[16]`
4. `test_flow_contract_cases[17]`
5. `test_flow_contract_cases[18]`
6. `test_flow_contract_cases[19]`
7. `test_flow_contract_cases[20]`
8. `test_flow_contract_cases[21]`
9. `test_flow_contract_cases[22]`

If the current Python-only `FlowCase` structure becomes too rigid for the blueprint-style flows, it is acceptable to split coverage into:

- `tests/integration/test_flow_contract_suite.py`
- `tests/integration/test_flow_yaml_contract_suite.py`

but only if the split is deliberate and documented.

## Flow YAML format expectations

Each new YAML flow file should include, at minimum:

- `id`
- `name`
- `purpose`
- `simulation_sources`
- `covers`
- `entry_conditions`
- `task_flow`
- `required_subtasks`
- `required_capabilities`
- `expected_tests`
- `known_limitations`

The YAML should remain descriptive and contract-oriented. It should not become a second hidden orchestration engine.

## Phase 1: Flow YAML Schema And Harness Preparation

### Purpose

Prepare the repository so flow YAML files are first-class checked assets instead of ad hoc documents.

### Work

- define the canonical YAML shape for `flows/*.yaml`
- decide whether current markdown flows remain alongside the YAML files or whether YAML becomes the new authoritative executable contract format
- add a lightweight loader/validator for flow YAML assets
- add note coverage so missing required keys in a flow YAML fail fast in tests

### Tests

- add unit coverage for flow YAML parsing and validation
- add a documentation/asset presence test asserting every new flow YAML parses successfully

### Exit criteria

- YAML flow files can be loaded deterministically
- missing required keys fail in tests with clear messages

### Current status

- Implemented:
  - repository-local strict flow YAML loader
  - required-key validation
  - filename/id matching validation
  - README/documentation updates for markdown-plus-YAML coexistence
  - unit coverage for valid and invalid flow YAML assets

## Phase 2: Project Bootstrap Flow

### Target files

- `flows/14_project_bootstrap_and_yaml_onboarding_flow.yaml`

### Purpose

Make project-local `.ai/` bootstrap and first compile a dedicated flow instead of an implied side path.

### Test scope

- create project-local policy/testing/docs/override YAML
- validate those YAML files
- compile the first node in the project
- inspect resolved workflow/source lineage

### Likely gaps to document if exposed

- missing project bootstrap CLI affordances
- weak project-local YAML discovery rules
- unresolved compile-source lineage for project-local assets

### Exit criteria

- the flow YAML exists
- a targeted pytest scenario executes the bootstrap path end to end

### Current status

- Implemented:
  - `flows/14_project_bootstrap_and_yaml_onboarding_flow.yaml`
  - `tests/integration/test_flow_yaml_contract_suite.py::test_flow_yaml_cases[14]`
  - temp-catalog bootstrap coverage for project policy, testing, override validation, first compile, and workflow source inspection
  - `tests/e2e/test_flow_14_project_bootstrap_and_yaml_onboarding_real.py`
  - real daemon/CLI coverage for project-local YAML validation, first compile, workflow sources, resolved YAML, and policy inspection

## Phase 3: Default Blueprint Flows

### Target files

- `flows/15_epic_default_workflow_blueprint_flow.yaml`
- `flows/16_phase_default_workflow_blueprint_flow.yaml`
- `flows/17_plan_default_workflow_blueprint_flow.yaml`
- `flows/18_task_default_workflow_blueprint_flow.yaml`

### Purpose

Make the built-in default node-kind task ladders explicit executable contracts instead of simulation-only narratives.

### Test scope

- compile each built-in node kind
- inspect the compiled task sequence
- assert required quality/provenance/docs/finalize stages appear in the correct order for each kind

### Likely gaps to document if exposed

- drift between built-in YAML and documented default ladders
- task ordering differences across compile outputs
- hidden hook/policy insertions that change the expected stage ladder

### Exit criteria

- one flow YAML per built-in node kind exists
- one test per blueprint verifies compiled order and required stage presence

### Current status

- Implemented:
  - `flows/15_epic_default_workflow_blueprint_flow.yaml`
  - `flows/16_phase_default_workflow_blueprint_flow.yaml`
  - `flows/17_plan_default_workflow_blueprint_flow.yaml`
  - `flows/18_task_default_workflow_blueprint_flow.yaml`
  - `tests/integration/test_flow_yaml_contract_suite.py::test_flow_yaml_cases[15]`
  - `tests/integration/test_flow_yaml_contract_suite.py::test_flow_yaml_cases[16]`
  - `tests/integration/test_flow_yaml_contract_suite.py::test_flow_yaml_cases[17]`
  - `tests/integration/test_flow_yaml_contract_suite.py::test_flow_yaml_cases[18]`
  - compile-order assertions locked to the current built-in ladders rather than the older wider simulation ladders
  - `tests/e2e/test_flow_15_to_18_default_blueprints_real.py`
  - real daemon/CLI compile proof for epic, phase, plan, and task blueprint ladders

### Real E2E hardening note for Flows 14 to 18

The first real subprocess pass for this slice exposed only test-contract mismatches:

- the initial project-local docs fixture for Flow 14 used an outdated `docs_definition`
  shape and had to be rewritten to match the real schema contract
- the initial blueprint tests assumed `workflow chain` was a task-level view, but the
  real runtime returns a subtask chain and task order must be compared after deduping

Those were corrected in the real E2E tests without requiring product changes.

## Phase 4: Hook Expansion Compile-Stage Flow

### Target files

- `flows/19_hook_expansion_compile_stage_flow.yaml`

### Purpose

Break hook expansion out of generic compile coverage and make its standalone contract explicit.

### Test scope

- provide built-in plus project hook inputs
- compile
- inspect hook selection, skipped hooks, ordering, and expanded workflow steps

### Likely gaps to document if exposed

- unstable hook ordering
- weak visibility into skipped-hook reasoning
- missing provenance/source capture for hook inputs

### Exit criteria

- dedicated YAML flow exists
- dedicated pytest verifies deterministic hook expansion

### Current status

- Implemented:
  - `flows/19_hook_expansion_compile_stage_flow.yaml`
  - `tests/integration/test_flow_yaml_contract_suite.py::test_flow_yaml_cases[19]`
  - dedicated hook-surface assertions for selected hooks, hook-policy payload, and expanded-step ordering
  - `tests/e2e/test_flow_19_hook_expansion_compile_stage_real.py`
  - strict real daemon/CLI subprocess coverage for compile-stage hook inspection
- Strict real-E2E gap coverage exposed:
  - the shipped task-node hook selection and expanded-step order differ from the older simulation-era expectation
  - the strict subprocess test is intentionally red until the desired hook contract is either implemented or the simulation-derived expectation is revised

## Phase 5: Compile Failure And Reattempt Flow

### Target files

- `flows/20_compile_failure_and_reattempt_flow.yaml`

### Purpose

Make compile failure, inspection, fix, and successful recompilation a first-class operator path.

### Test scope

- compile with a malformed in-scope project policy YAML
- assert durable compile failure state
- inspect compile-failure evidence
- fix the source
- recompile successfully

### Likely gaps to document if exposed

- insufficient compile-failure evidence
- failure state not clearing cleanly after successful reattempt
- ambiguous node-version or workflow pointer state after retry

### Exit criteria

- the full failure-to-reattempt path has a dedicated flow YAML and passing pytest

### Current status

- Implemented:
  - `flows/20_compile_failure_and_reattempt_flow.yaml`
  - `tests/integration/test_flow_yaml_contract_suite.py::test_flow_yaml_cases[20]`
  - contract coverage for schema-validation compile failure, durable failure inspection, source repair, and successful recompile of the same node
  - `tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py`
  - strict real daemon/CLI subprocess coverage for failure, inspection, repair, and recompile
- Issues exposed and documented during implementation:
  - the compile endpoint returns HTTP `200` with `status = failed` and `compile_failure` payload, rather than surfacing compile failure as an HTTP error response
  - the YAML flow contract suite needed an explicit `migrated_public_schema` dependency to avoid hidden test-order coupling during isolated runs
  - the strict real-E2E test now shows that `workflow source-discovery --node ...` still returns `compiled workflow not found` after a failed compile, so there is no source-discovery inspection surface for compile-failed nodes yet

## Phase 6: Child Session Round-Trip And Merge-Back Flow

### Target files

- `flows/21_child_session_round_trip_and_mergeback_flow.yaml`

### Purpose

Make pushed child work and structured merge-back a standalone flow rather than an embedded recovery subcase.

### Test scope

- push child session
- emit structured child result
- validate and persist the result
- reattach it to parent context
- verify parent remains on the same compiled subtask

### Likely gaps to document if exposed

- unstable parent context merge-back semantics
- weak result validation contract
- inadequate inspection of child-result lineage

### Exit criteria

- flow YAML exists
- pytest verifies bounded child round-trip behavior end to end

### Current status

- Implemented:
  - `flows/21_child_session_round_trip_and_mergeback_flow.yaml`
  - `tests/integration/test_flow_yaml_contract_suite.py::test_flow_yaml_cases[21]`
  - daemon-backed child-session push/pop/result/context coverage with explicit parent-subtask retention assertions
- Strict real-E2E gap coverage added:
  - `tests/e2e/test_flow_21_child_session_round_trip_and_mergeback_real.py`
  - this test intentionally does not inject a synthetic `session pop` payload
  - it waits for a live tmux/Codex child session to produce durable merge-back state
  - it is expected to fail until the runtime launches Codex rather than an interactive shell
  - the current failure shows the tmux child pane still contains raw delegated prompt text and a shell prompt, not a Codex-launched child agent

## Phase 7: Dependency-Blocked Sibling Wait Flow

### Target files

- `flows/22_dependency_blocked_sibling_wait_flow.yaml`

### Purpose

Make the canonical “one sibling blocked on another” path explicit and testable as its own flow.

### Test scope

- materialize sibling children with a valid dependency edge
- admit/start the ready child
- verify the dependent sibling remains blocked
- inspect blocker explanation and readiness transition after completion

### Likely gaps to document if exposed

- weak blocker explanations
- incorrect sibling state transitions
- missing impossible-wait escalation when the dependency cannot complete

### Exit criteria

- flow YAML exists
- pytest verifies blocked, then unblocked sibling behavior

### Current status

- Implemented:
  - `flows/22_dependency_blocked_sibling_wait_flow.yaml`
- `tests/integration/test_flow_yaml_contract_suite.py::test_flow_yaml_cases[22]`
- explicit sibling dependency add/blocked-start/unblocked-start coverage
- Strict real-E2E gap coverage added:
  - `tests/e2e/test_flow_22_dependency_blocked_sibling_wait_real.py`
  - this test intentionally does not force sibling completion via lifecycle mutation
  - it waits for the dependency sibling to complete through a live tmux/Codex session path
  - it is expected to fail until the runtime launches Codex and can observe real completion from the live session
  - the first strict run also exposed a blocker/admission gap: the dependent sibling was still startable in the tested sibling-dependency scenario
  - `tests/integration/test_flow_yaml_contract_suite.py::test_flow_yaml_cases[22]`
  - daemon-backed sibling dependency validation, blocker inspection, blocked admission, and post-completion admission coverage

## Phase 8: Flow README And Traceability Update

### Purpose

Bring the flow inventory and traceability notes into sync after the new YAML assets and tests exist.

### Work

- update `flows/README.md`
- update `notes/catalogs/traceability/simulation_flow_union_inventory.md`
- update any per-flow planning/checklist note that refers to the missing-flow set

### Tests

- note/documentation quickstart tests
- any new asset-presence tests for flow YAML files

### Exit criteria

- the new flows are discoverable
- the simulations-to-flows gap note no longer lists them as missing

## Recommended execution order

1. Phase 1: Flow YAML Schema And Harness Preparation
2. Phase 2: Project Bootstrap Flow
3. Phase 3: Default Blueprint Flows
4. Phase 4: Hook Expansion Compile-Stage Flow
5. Phase 5: Compile Failure And Reattempt Flow
6. Phase 6: Child Session Round-Trip And Merge-Back Flow
7. Phase 7: Dependency-Blocked Sibling Wait Flow
8. Phase 8: Flow README And Traceability Update

## Why this order

- Phase 1 prevents ad hoc YAML drift before multiple flow assets are added.
- Project bootstrap and blueprint flows are mostly descriptive compile/read contracts and should stabilize the harness first.
- Hook expansion and compile failure build directly on compile-stage coverage.
- Child-session and dependency-blocked-sibling flows are more stateful runtime contracts and should come after the harness and compile-centric flow assets are stable.
