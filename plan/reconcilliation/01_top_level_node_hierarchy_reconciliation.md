# Top-Level Node Hierarchy Reconciliation

## Scope

Reconcile the current implementation with the documented doctrine that top-ness is structural rather than semantic.

The intended rule is:

- any node kind may be created as a top node when it has no parent
- that creation is valid only when the hierarchy definition for that kind sets `allow_parentless: true`

## Rationale

Current notes now clarify the doctrine above, but the shipped built-in hierarchy and startup tests still enforce an `epic`-only top-level path.

That drift currently exists in:

- built-in node YAML under `src/aicoding/resources/yaml/builtin/system-yaml/nodes/`
- workflow-start tests under `tests/unit/test_workflow_start.py` and `tests/integration/test_workflow_start_flow.py`
- bounded and real-E2E Flow 01 coverage

## Related Notes And Specs

- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/planning/implementation/top_level_workflow_creation_commands_decisions.md`
- `notes/planning/implementation/scenario_and_flow_pytest_plan.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`

## Affected Systems

- Database: `affected`
- CLI: `affected`
- Daemon: `affected`
- YAML: `affected`
- Prompts: `possibly_affected`

Prompt assets may not need changes if the existing node-kind prompts remain valid when a kind is parentless.

## Current Drift Summary

### Doctrine

- top-ness is defined by the absence of a parent
- any kind may be top-level when its hierarchy definition allows `allow_parentless: true`

### Current shipped behavior

- only `epic.yaml` currently sets `allow_parentless: true`
- `phase.yaml`, `plan.yaml`, and `task.yaml` currently require a parent
- workflow-start tests explicitly reject a non-top-level `task`

## Invariants To Preserve

1. Top-level legality must be determined only by hierarchy YAML plus daemon validation.
2. The daemon and CLI must not hardcode `epic` as the only top-level kind.
3. Parentless creation must remain inspectable through durable node, version, lifecycle, and workflow records.
4. Built-in defaults may prefer one semantic ladder without forbidding other parentless starts.
5. Flow 01 proof must match the same doctrinal rule used by the hierarchy loader.

## Non-Goals

- automatic kind inference from prompt content
- changing default decomposition layouts unless required by parentless operation
- expanding prompt packs beyond what parentless creation actually needs

## Expected Test Layers

- unit
- integration
- real E2E
- document consistency

## Canonical Verification Commands

Document consistency after note/plan updates:

```bash
python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_verification_command_docs.py tests/unit/test_flow_e2e_alignment_docs.py tests/unit/test_notes_quickstart_docs.py
```

Hierarchy and startup behavior after implementation:

```bash
python3 -m pytest tests/unit/test_workflow_start.py tests/integration/test_workflow_start_flow.py tests/integration/test_flow_contract_suite.py -q
```

Real top-level startup proof after implementation:

```bash
python3 -m pytest tests/e2e/test_flow_01_create_top_level_node_real.py -q
```

## Completion Criteria

This reconciliation is complete only when all of the following are true:

1. Built-in hierarchy YAML expresses the intended parentless rule deliberately.
2. The hierarchy loader and workflow-start path accept every built-in kind that is intentionally marked `allow_parentless: true`.
3. Tests no longer encode `epic` as the sole doctrinal top-level kind.
4. Flow 01 bounded and real-E2E coverage state is updated honestly.
5. Walkthroughs and implementation notes describe the same rule as the code.

## Phases

### Phase 1: Built-In Hierarchy Decision

Decide which built-in kinds should ship with `allow_parentless: true`.

Required outputs:

- explicit decision note or direct YAML change
- matching update to the startup-flow documentation

Open choice:

- allow all built-in kinds to be parentless by default
- allow a smaller built-in subset to be parentless, while preserving the doctrine that any custom kind may also be parentless when configured that way

### Phase 2: YAML And Loader Reconciliation

Update the built-in node YAML and confirm the runtime already honors the resulting `allow_parentless` set through the hierarchy registry.

Likely files:

- `src/aicoding/resources/yaml/builtin/system-yaml/nodes/epic.yaml`
- `src/aicoding/resources/yaml/builtin/system-yaml/nodes/phase.yaml`
- `src/aicoding/resources/yaml/builtin/system-yaml/nodes/plan.yaml`
- `src/aicoding/resources/yaml/builtin/system-yaml/nodes/task.yaml`

### Phase 3: CLI And Daemon Startup Reconciliation

Remove test and handler assumptions that effectively freeze top-level startup to `epic`.

Likely files:

- `tests/unit/test_workflow_start.py`
- `tests/integration/test_workflow_start_flow.py`
- daemon or CLI startup handlers if they still encode semantic assumptions

### Phase 4: Flow Proof Reconciliation

Update Flow 01 bounded and real-E2E coverage so it proves the intended rule rather than one semantic example.

Required outcomes:

- at least one additional top-level startup variant if multiple built-in kinds are parentless
- honest status in `flow_coverage_checklist.md`

### Phase 5: Walkthrough Reconciliation

Refresh the node-kind walkthrough docs once the built-in hierarchy is settled.

Required outcomes:

- `epic`, `phase`, `plan`, and `task` docs all describe top-ness consistently
- node-kind examples distinguish doctrinal rule from one default built-in ladder

## Risks

- enabling too many built-in parentless kinds without tightening walkthroughs could make the default operator story less coherent
- leaving tests on the old `epic` assumption will recreate note drift immediately
- parentless `task` starts may expose prompt or quality-gate assumptions that were only exercised under a `plan` parent

## Status

- overall status: `planned`
- implementation status: `blocked_on_reconciliation_decision`
- proving status: `partial`
