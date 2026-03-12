# Workflow Profile Support Gap Closure

## Purpose

Capture the concrete support delta between:

- the workflow-overhaul future notes

and:

- the current implemented code, CLI, daemon, and YAML model

This is a working note, not an implementation claim.

One of the required closed gaps is now explicit:

- non-leaf tiers must have rigid daemon-enforced step order
- skipped decomposition, merge, or completion steps must fail with concrete blocked mutations
- subtask completion must rely on explicit durable predicates rather than narrative interpretation alone

## Current State Summary

The current implementation already has:

- stable node kinds: `epic`, `phase`, `plan`, `task`
- daemon-backed node creation and workflow start
- built-in layout materialization
- immutable compile snapshots
- node-kind inspection
- run, lifecycle, and compiled-workflow inspection

The current implementation does not yet have:

- workflow-profile definitions
- profile-aware node definitions
- profile-aware layout definitions
- node/version/profile persistence
- CLI/API profile selection
- profile inspection commands
- compiler validation for profile/layout compatibility
- compiler-generated epic briefs

## Existing Support

### Database

Exists now:

- kind-level hierarchy definition persistence
- node rows with `kind`, `tier`, `title`, and `prompt`
- compiled workflow persistence

Relevant current surfaces:

- `src/aicoding/db/models.py`
- `src/aicoding/daemon/hierarchy.py`
- `src/aicoding/daemon/workflows.py`

### CLI

Exists now:

- `workflow start`
- `node create`
- `node kinds`
- `node materialize-children`
- workflow compile and inspection surfaces

Relevant current surfaces:

- `src/aicoding/cli/parser.py`
- `src/aicoding/cli/handlers.py`
- `notes/specs/cli/cli_surface_spec_v2.md`

### Daemon

Exists now:

- create/start endpoints
- materialization endpoints
- node-kind listing endpoint
- compile/runtime inspection endpoints

Relevant current surfaces:

- `src/aicoding/daemon/app.py`
- `src/aicoding/daemon/workflow_start.py`
- `src/aicoding/daemon/materialization.py`
- `src/aicoding/daemon/workflows.py`

### YAML

Exists now:

- `node_definition`
- `layout_definition`
- built-in nodes and layouts

Relevant current surfaces:

- `src/aicoding/yaml_schemas.py`
- `src/aicoding/hierarchy.py`
- `src/aicoding/resources/yaml/builtin/system-yaml/nodes/*.yaml`
- `src/aicoding/resources/yaml/builtin/system-yaml/layouts/*.yaml`

## Main Gap

The future notes assume node variants implemented as workflow profiles layered on top of stable kinds.

The active runtime still treats:

- node behavior as kind-owned
- layout selection as fixed by kind
- node creation as kind plus prompt only

That means the notes currently outrun the code in a predictable way.

## Proposed Note Updates

The following note families would need updates when implementation begins.

### CLI notes

Update:

- `notes/specs/cli/cli_surface_spec_v2.md`

Add or revise sections for:

- `workflow start --workflow-profile <id>`
- `node create --workflow-profile <id>`
- `node materialize-children --layout <id>`
- `node materialize-children --workflow-profile <id>`
- `workflow profiles list`
- `workflow profiles show --profile <id>`
- `workflow brief --node <id>`
- layout inspection and mutation commands that become materially important once profiles choose layouts

### Runtime notes

Update:

- `notes/specs/runtime/node_lifecycle_spec_v2.md`

Add or revise sections for:

- where selected workflow profile is frozen
- how profile/layout compatibility is validated
- how required child roles are validated
- how completion-claim restrictions become runtime-visible
- how compiler-generated epic briefs are persisted and inspected
- how the brief composes node-tier prompt, profile prompt, recommended child profiles with descriptions, and CLI discovery guidance

### Architecture notes

Update:

- `notes/specs/architecture/code_vs_yaml_delineation.md`

Clarify:

- profiles, roles, and layout compatibility stay declarative in YAML
- legality checks, balancing, completion gating, and compilation remain code-owned

### Future-plan notes

Update:

- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/project_skeleton_generator/2026-03-10_workflow_overhaul_integration.md`

When implementation opens, these notes should point to the authoritative task plans, feature plans, and schema decisions that actually adopt the workflow-profile model.

## Proposed YAML Changes

### New family

Add a new YAML family:

- `workflow_profile_definition`

Likely file area:

- `src/aicoding/resources/yaml/schemas/workflow_profile_definition.yaml`
- `src/aicoding/resources/yaml/builtin/system-yaml/workflow_profiles/*.yaml`

### Extend node definitions

Extend `node_definition` to support:

- `default_workflow_profile`
- `supported_workflow_profiles`
- `main_prompt_ref` or equivalent normalized prompt reference naming

### Extend layout definitions

Extend `layout_definition` and layout children to support:

- `profile`
- `compatible_workflow_profiles`
- `layout_tags`
- child `role`
- child `workflow_profile`
- child `expected_outputs`
- child `required_updates`
- child `verification_targets`
- child `estimated_points`

## Proposed Backend Changes

### Persistence

Add persistence for:

- selected workflow profile on node version or compiled workflow context
- profile-aware hierarchy metadata where inspection needs it
- generated epic brief or equivalent compiled summary payload

Recommended first choice:

- freeze selected profile and profile-derived obligations into compiled workflow context first
- avoid widening durable node tables unless read/write behavior proves that a dedicated column is needed

### Compiler

Add compiler support for:

- resolving selected workflow profiles
- validating that the profile applies to the selected kind
- validating that the selected layout is compatible with the selected profile
- validating required child roles
- freezing required updates and verification targets into compiled payloads
- generating the epic brief from the selected profile and effective layout
- embedding:
  - node-tier prompt
  - selected profile prompt
  - recommended child profiles with descriptions
  - a CLI note for discovering the full available child-profile set

### Materialization

Replace fixed kind-to-layout-only behavior with:

- selected profile default layout resolution
- optional explicit layout override resolution
- compatibility validation between node kind, selected profile, and chosen layout

### Hierarchy inspection

Enrich hierarchy read paths so they can expose:

- default workflow profile per kind
- supported workflow profiles per kind
- selected workflow profile per node/version where applicable

## Proposed CLI/API Changes

### Extend existing commands

Add support to:

- `workflow start --workflow-profile <id>`
- `node create --workflow-profile <id>`
- `node create --layout <id>` if explicit layout selection is allowed at create time
- `node materialize-children --workflow-profile <id>`
- `node materialize-children --layout <id>`

### New inspection commands

Add:

- `workflow profiles list`
- `workflow profiles show --profile <id>`
- `workflow brief --node <id>`
- `node types --node <id>`
- `node profiles --node <id>`
- `node profile show --node <id>` or equivalent
- `node kinds --verbose` or equivalent profile-aware enriched output

### Layout family commands

The CLI spec already suggests layout commands.

These become much more important under the workflow-profile model:

- `layout show --node <id>`
- `layout generate --node <id>`
- `layout update --node <id>`
- `layout validate --node <id>`

## Proposed API Changes

Likely new or revised daemon payload fields:

- `WorkflowStartRequest.workflow_profile`
- `NodeCreateRequest.workflow_profile`
- `HierarchyNodeResponse.workflow_profile`
- `NodeKindDefinitionResponse.default_workflow_profile`
- `NodeKindDefinitionResponse.supported_workflow_profiles`
- `MaterializationResponse.selected_layout_id`
- `MaterializationResponse.selected_workflow_profile`
- compiled workflow response fields for profile-derived metadata

Likely new endpoints:

- `GET /api/workflow-profiles`
- `GET /api/workflow-profiles/{profile_id}`
- `GET /api/nodes/{node_id}/workflow-brief`
- `GET /api/nodes/{node_id}/types`
- `GET /api/nodes/{node_id}/profiles`

Response rule for the future `node types` surface:

- return descriptions, not ids alone, for kinds, profiles, layouts, and child roles

Relationship to brief generation:

- the brief should expose the recommended child-profile subset
- the CLI type/profile surfaces should expose the fuller legal option set

## Proposed Prompt Changes

The profile model implies prompt changes, but these should remain secondary to structural adoption.

Likely prompt work:

- generic and profile-specific layout prompts
- profile-specific epic decomposition prompts
- compiler-generated brief rendering prompts only if needed for the final brief format

The runtime should not depend on prompts alone to know what profile behavior means.

## Proposed Tests

### Unit

Add tests for:

- workflow profile schema validation
- node definition support for default and supported profiles
- layout/profile compatibility checks
- required-role validation
- compiler-generated brief formation

### Integration

Add tests for:

- daemon create/start with workflow profile selection
- profile-aware materialization
- profile-aware node-kind inspection
- layout override or compatibility failure paths

### CLI

Add tests for:

- parser coverage for new `--workflow-profile` and `--layout` flags
- new profile inspection commands
- enriched `node kinds` or equivalent output

### E2E

Add at least one real narrative proving:

- a selected top-level profile drives decomposition into the expected role bands
- the resulting child nodes are inspectable as profile-aligned variants

## Performance And Auditability

Profile support will touch compile and materialization hot paths.

Implementation should review:

- extra compile-stage validation cost
- layout/profile lookup cost
- operator inspection payload size growth
- whether profile-derived obligations remain explainable through existing audit surfaces

## Suggested Implementation Order

1. YAML schema and resource-family adoption
2. compiler and validation support
3. persistence and inspection payload enrichment
4. CLI/API selection and inspection commands
5. layout command family completion
6. real E2E proof for profile-driven decomposition

## Immediate Recommendation

When authoritative implementation planning begins, open one task or feature plan specifically for:

- workflow-profile schema and compiler adoption

Do not split CLI naming decisions away from the compiler and YAML model too early.

The command surface should follow the adopted data model, not guess ahead of it.
