# Proposed Note And Code Updates

## Purpose

Write down the concrete proposed updates that would be needed to move the workflow-overhaul idea from future-note form toward implementable repository changes.

This note stays inside the workflow-overhaul working-note bundle on purpose.

It is not an implementation claim.

## How To Read This Note

This note is organized as:

1. proposed note updates
2. proposed code updates
3. proposed command-surface additions
4. proposed proving additions

Use it as the practical companion to:

- `2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `2026-03-10_workflow_profile_support_gap_closure.md`

## Proposed Note Updates

### `notes/specs/architecture/code_vs_yaml_delineation.md`

Add a section for workflow-profile ownership.

Proposed additions:

- `workflow_profile_definition` is declarative YAML
- profile-to-layout compatibility is declared in YAML
- child roles, expected outputs, required updates, and verification targets are declared in YAML
- legality checks, profile applicability, compatibility enforcement, balance enforcement, completion gating, and compiled-brief generation remain code-owned

Reason:

- the workflow-overhaul note explicitly wants profiles declarative and enforcement code-owned

### `notes/specs/cli/cli_surface_spec_v2.md`

Add workflow-profile-aware command sections.

Proposed new or revised command docs:

- `workflow start --workflow-profile <id>`
- `node create --workflow-profile <id>`
- `node create --layout <id>`
- `node materialize-children --workflow-profile <id>`
- `node materialize-children --layout <id>`
- `workflow profiles list`
- `workflow profiles show --profile <id>`
- `workflow brief --node <id>`
- `node kinds --verbose` showing default and supported profiles
- `layout show --node <id>`
- `layout validate --node <id>`
- `layout update --node <id>`
- `layout generate --node <id>`

Reason:

- profile-aware nodes become hard to inspect or drive without profile and layout surfaces

### `notes/specs/runtime/node_lifecycle_spec_v2.md`

Add compile/runtime sections for profile-aware execution.

Proposed additions:

- selected workflow profile becomes frozen compile context
- profile/layout compatibility is checked during compile or materialization
- required child-role coverage is a compiler-visible invariant
- completion restrictions derived from selected profile are inspectable at runtime
- compiler-generated epic brief is a persisted and inspectable artifact
- the brief context should include node-tier prompt, selected profile prompt, recommended child profiles with descriptions, and a CLI discovery note for the broader available child-profile set

Reason:

- the current future notes make these runtime expectations explicit, but the runtime spec does not yet say where they live

### `notes/specs/yaml/yaml_schemas_spec_v2.md`

Add schema-family coverage for workflow profiles and richer layouts.

Proposed additions:

- `workflow_profile_definition` family
- extended `node_definition` fields:
  - `default_workflow_profile`
  - `supported_workflow_profiles`
  - normalized prompt-reference field naming
- extended `layout_definition` fields:
  - top-level `profile`
  - `compatible_workflow_profiles`
  - `layout_tags`
- extended layout child fields:
  - `role`
  - `workflow_profile`
  - `expected_outputs`
  - `required_updates`
  - `verification_targets`
  - `estimated_points`

Reason:

- the current schema note needs to become the contract for these additions instead of leaving them only in a future-plan note

### `notes/catalogs/checklists/verification_command_catalog.md`

Add canonical commands once profile support lands.

Expected future command entries:

- schema tests for workflow-profile docs
- unit tests for profile/layout compatibility
- integration tests for profile-aware create/start/materialize flows
- E2E suite for profile-driven decomposition

Reason:

- the repo doctrine requires canonical commands to be documented, not rediscovered

### `notes/catalogs/checklists/e2e_execution_policy.md`

Add coverage language for profile-driven decomposition.

Proposed additions:

- profile selection alone does not count as flow proof
- real E2E must exercise chosen profile through real CLI/daemon/compiler/materialization paths

Reason:

- workflow profiles change planning and decomposition behavior, so their proving rules need to be explicit

## Proposed Code Updates

### `src/aicoding/yaml_schemas.py`

Add new models and extend existing ones.

Proposed changes:

- add `WorkflowProfileDefinitionDocument`
- extend `NodeDefinition` with:
  - `default_workflow_profile`
  - `supported_workflow_profiles`
  - prompt-ref naming cleanup if adopted
- extend `LayoutDefinitionDocument` and `LayoutChildDefinition` with profile-aware fields
- register the new family in `FAMILY_MODELS`
- update family identification and validation helpers

Reason:

- without schema support, the rest of the stack cannot adopt the profile model safely

### `src/aicoding/hierarchy.py`

Teach hierarchy loading and validation about profiles.

Proposed changes:

- load supported/default workflow profile metadata from node definitions
- expose profile-aware kind inspection helpers
- add validation that selected profiles are allowed for a kind

Reason:

- the current hierarchy registry only understands kind-level structure

### `src/aicoding/structural_library.py`

Extend structural-library validation.

Proposed changes:

- require the new `workflow_profiles/` family once adopted
- validate node definitions against referenced profiles
- validate layouts against compatible profiles
- validate child `workflow_profile` references and role coverage hints

Reason:

- this repo treats built-in libraries as implementation assets and expects broken references to be caught mechanically

### `src/aicoding/daemon/workflows.py`

Add compiler support for workflow profiles.

Proposed changes:

- resolve selected workflow profile for a node/version
- validate profile applicability to the node kind
- validate layout compatibility with selected profile
- validate required child-role coverage
- freeze selected profile, required updates, verification targets, and related profile metadata into compiled workflow context
- generate and freeze the compiler-generated epic brief
- assemble the brief from:
  - node-tier prompt
  - selected profile prompt
  - recommended child profiles with descriptions
  - a CLI discovery note for `node types` / `node profiles`

Reason:

- the workflow-overhaul note expects the compiler to be authoritative for these checks

### `src/aicoding/daemon/materialization.py`

Replace fixed kind-only layout selection with profile-aware selection.

Proposed changes:

- resolve default layout from selected workflow profile when present
- allow explicit layout override when the command surface supports it
- validate selected layout against chosen profile
- surface selected profile and selected layout in materialization responses

Reason:

- current materialization hardcodes `kind -> layout`
- the workflow-overhaul note says profile should select layout and child-role expectations

### `src/aicoding/daemon/models.py`

Extend request and response models.

Proposed request additions:

- `WorkflowStartRequest.workflow_profile`
- `WorkflowStartRequest.layout_id` if allowed
- `NodeCreateRequest.workflow_profile`
- `NodeCreateRequest.layout_id` if allowed

Proposed response additions:

- `HierarchyNodeResponse.workflow_profile`
- `NodeKindDefinitionResponse.default_workflow_profile`
- `NodeKindDefinitionResponse.supported_workflow_profiles`
- `MaterializationResponse.selected_workflow_profile`
- `MaterializationResponse.selected_layout_id`
- compiled workflow response fields for profile-derived metadata and brief content

Reason:

- the current API cannot carry the profile-aware state the future notes require

### `src/aicoding/daemon/app.py`

Add new endpoints and extend existing ones.

Proposed endpoint changes:

- extend `/api/workflows/start`
- extend `/api/nodes/create`
- extend `/api/node-kinds`
- add `/api/workflow-profiles`
- add `/api/workflow-profiles/{profile_id}`
- add `/api/nodes/{node_id}/workflow-brief`

Reason:

- the CLI should not have to infer profile state by inspecting raw YAML or full compiled payloads only

### `src/aicoding/cli/parser.py`

Add CLI flags and subcommands.

Proposed changes:

- add `--workflow-profile` to `workflow start`
- add `--workflow-profile` to `node create`
- add `--layout` to `node create` if supported
- add `--workflow-profile` and `--layout` to `node materialize-children`
- add `workflow profiles list`
- add `workflow profiles show`
- add `workflow brief`
- add `layout` command group if that adoption is approved

Reason:

- the workflow-overhaul model needs user-visible and AI-visible automation paths

### `src/aicoding/cli/handlers.py`

Add handler support for the new endpoints and enrich existing output.

Proposed changes:

- pass through profile and layout selectors on create/start/materialize commands
- add workflow-profile list/show handlers
- add workflow-brief handler
- enrich `node kinds` output with profile metadata

Reason:

- the current handlers only pass kind/title/prompt selectors

### `src/aicoding/db/models.py`

Add persistence only where needed.

Conservative proposal:

- prefer freezing selected workflow profile and brief data into compiled workflow context first
- add dedicated columns only if read/query needs justify them

Possible future columns if needed:

- selected workflow profile on node versions
- selected workflow profile on hierarchy nodes if creation-time visibility requires it

Reason:

- avoid widening durable schema earlier than necessary

## Proposed Command-Surface Additions

### Commands that should likely be added

- `workflow profiles list`
- `workflow profiles show --profile <id>`
- `workflow brief --node <id>`
- `node types --node <id>`
- `node profiles --node <id>`

### Existing commands that likely need extension

- `workflow start`
- `node create`
- `node kinds`
- `node materialize-children`
- `workflow show`

### Commands already suggested in existing CLI notes that become more urgent

- `layout generate`
- `layout show`
- `layout update`
- `layout validate`

## Proposed `node types` Contract

The workflow-overhaul command surface should include:

- `node types --node <id>`

Purpose:

- tell an operator or AI contributor what workflow-profile-aware node variants are available from the current node context

This command should not return opaque ids only.

It should return descriptions for all user-facing selectable or inspectable items.

Minimum recommended response content:

- current node kind id and description
- selected workflow profile id, name, and description when one is already set
- default workflow profile id, name, and description when no explicit profile is set
- supported workflow profiles with:
  - id
  - name
  - description
- compatible layouts with:
  - id
  - name
  - description
- allowed child kinds with descriptions where available
- required child roles with:
  - role id
  - role description
  - default child workflow profile id
  - default child workflow profile description

Suggested response shape:

```json
{
  "node_id": "…",
  "kind": {
    "id": "epic",
    "description": "Top-level outcome-oriented planning container."
  },
  "selected_workflow_profile": {
    "id": "epic.feature",
    "name": "Feature Epic",
    "description": "Deliver a feature through discovery, implementation, docs alignment, and real proof."
  },
  "supported_workflow_profiles": [
    {
      "id": "epic.planning",
      "name": "Planning Epic",
      "description": "Turn rough intent into explicit requirements, architecture, and verification mapping."
    },
    {
      "id": "epic.feature",
      "name": "Feature Epic",
      "description": "Deliver a feature through discovery, implementation, docs alignment, and real proof."
    }
  ],
  "compatible_layouts": [
    {
      "id": "epic_feature_to_phases",
      "name": "Feature Epic To Phases",
      "description": "Standard feature-delivery epic breakdown."
    }
  ],
  "child_roles": [
    {
      "role": "discovery",
      "description": "Clarify scope, invariants, and implementation boundaries.",
      "default_profile": {
        "id": "phase.discovery",
        "name": "Discovery Phase",
        "description": "Clarify scope, invariants, risks, and implementation boundaries before execution."
      }
    }
  ]
}
```

Companion command:

- `node profiles --node <id>`

Suggested purpose:

- a narrower profile-focused read when callers do not need the full type/layout/role bundle

Relationship to generated briefs:

- generated workflow briefs should include recommended child profiles and their descriptions
- generated workflow briefs should also tell the caller to use `node types --node <id>` when it needs the full available child-profile set instead of only the recommendation

## Proposed Test Updates

### Unit tests

Add or extend:

- `tests/unit/test_yaml_schemas.py`
- `tests/unit/test_structural_library.py`
- new workflow-profile compiler tests
- new profile/layout compatibility tests

### Integration tests

Add:

- profile-aware workflow start flow
- profile-aware node creation flow
- profile-aware materialization flow
- workflow-profile inspection endpoint coverage

### CLI tests

Add:

- parser coverage for new flags and commands
- handler coverage for profile-aware payloads

### E2E tests

Add at least one real flow where:

- a selected top-level profile leads to the expected phase-role decomposition
- the chosen profile and selected layout remain inspectable afterward

## Suggested Adoption Order

1. note and schema updates
2. YAML schema models and built-in profile family
3. compiler and materialization support
4. API and CLI selection/inspection surfaces
5. real E2E proof

## Immediate Working Recommendation

If implementation planning starts soon, split the work into three authoritative implementation tracks:

1. workflow-profile schema and compiler adoption
2. profile-aware CLI/API and layout-command surfaces
3. real E2E proof for profile-driven decomposition

That split matches the actual risk boundaries better than one giant feature ticket.
