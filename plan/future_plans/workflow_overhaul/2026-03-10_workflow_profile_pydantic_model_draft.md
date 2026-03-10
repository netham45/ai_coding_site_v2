# Workflow Profile Pydantic Model Draft

## Purpose

Map the workflow-profile response-shape drafts onto a likely future `src/aicoding/daemon/models.py` model set.

This is a working-note draft for the workflow-overhaul bundle.

It is not an adopted implementation.

## Goal

The goal of this note is to reduce the gap between:

- high-level workflow-overhaul prose
- JSON payload examples
- future daemon model code

## Design Approach

Use shared descriptor models first.

Then build:

- `WorkflowBriefResponse`
- `NodeTypesResponse`
- `NodeProfilesResponse`

on top of those shared descriptors.

This keeps the daemon response surface consistent and keeps CLI handlers thin.

## Recommended Shared Descriptor Models

### `KindDescriptorResponse`

```python
class KindDescriptorResponse(AICodingModel):
    id: str
    name: str
    description: str
```

Purpose:

- reusable kind descriptor across brief, types, and profile responses

### `WorkflowProfileDescriptorResponse`

```python
class WorkflowProfileDescriptorResponse(AICodingModel):
    id: str
    name: str
    description: str
    main_prompt_ref: str | None = None
    default_child_layout: str | None = None
```

Purpose:

- reusable profile descriptor for both compact and fuller profile reads

### `LayoutDescriptorResponse`

```python
class LayoutDescriptorResponse(AICodingModel):
    id: str
    name: str
    description: str
```

Purpose:

- reusable layout descriptor for compatible-layout and selected-layout reads

### `RoleDescriptorResponse`

```python
class RoleDescriptorResponse(AICodingModel):
    role: str
    description: str
```

Purpose:

- reusable child-role descriptor

### `AllowedChildKindDescriptorResponse`

```python
class AllowedChildKindDescriptorResponse(AICodingModel):
    id: str
    description: str
```

Purpose:

- reusable descriptor for allowed child kinds in `node types`

## Recommended Composite Models

### `RecommendedChildProfileResponse`

```python
class RecommendedChildProfileResponse(AICodingModel):
    role: str
    description: str
    workflow_profile: WorkflowProfileDescriptorResponse
```

Purpose:

- one recommended role-to-profile item in `workflow brief`

### `NodeTypeChildRoleResponse`

```python
class NodeTypeChildRoleResponse(AICodingModel):
    role: str
    description: str
    recommended_workflow_profile: WorkflowProfileDescriptorResponse | None = None
```

Purpose:

- one role row in `node types`

### `ProfileRequiredRoleResponse`

```python
class ProfileRequiredRoleResponse(AICodingModel):
    role: str
    description: str
```

Purpose:

- one required role row inside a fuller profile record

### `WorkflowBriefPromptStackResponse`

```python
class WorkflowBriefPromptStackResponse(AICodingModel):
    node_tier_prompt_ref: str | None = None
    workflow_profile_prompt_ref: str | None = None
    brief_prompt_ref: str | None = None
```

Purpose:

- expose the multi-part prompt stack without forcing raw prompt inspection

### `WorkflowBriefCliDiscoveryNoteResponse`

```python
class WorkflowBriefCliDiscoveryNoteResponse(AICodingModel):
    summary: str
    commands: list[str]
```

Purpose:

- carry the CLI discovery guidance required by the workflow-overhaul notes

## Recommended Top-Level Responses

### `WorkflowBriefResponse`

```python
class WorkflowBriefResponse(AICodingModel):
    node_id: str
    kind: KindDescriptorResponse
    workflow_profile: WorkflowProfileDescriptorResponse
    objective: str
    prompt_stack: WorkflowBriefPromptStackResponse
    selected_layout: LayoutDescriptorResponse | None = None
    recommended_children: list[RecommendedChildProfileResponse]
    required_repository_updates: list[str] = Field(default_factory=list)
    required_verification: list[str] = Field(default_factory=list)
    cli_discovery_note: WorkflowBriefCliDiscoveryNoteResponse
```

Purpose:

- operator-facing and AI-facing summary of current node objective and recommended decomposition posture

### `NodeTypesResponse`

```python
class NodeTypesResponse(AICodingModel):
    node_id: str
    kind: KindDescriptorResponse
    selected_workflow_profile: WorkflowProfileDescriptorResponse | None = None
    default_workflow_profile: WorkflowProfileDescriptorResponse | None = None
    supported_workflow_profiles: list[WorkflowProfileDescriptorResponse] = Field(default_factory=list)
    compatible_layouts: list[LayoutDescriptorResponse] = Field(default_factory=list)
    allowed_child_kinds: list[AllowedChildKindDescriptorResponse] = Field(default_factory=list)
    child_roles: list[NodeTypeChildRoleResponse] = Field(default_factory=list)
```

Purpose:

- broader structural/type catalog for the current node context

### `NodeProfileDetailResponse`

```python
class NodeProfileDetailResponse(AICodingModel):
    id: str
    name: str
    description: str
    main_prompt_ref: str | None = None
    default_child_layout: str | None = None
    required_child_roles: list[ProfileRequiredRoleResponse] = Field(default_factory=list)
```

Purpose:

- fuller per-profile row for the `node profiles` surface

### `NodeProfilesResponse`

```python
class NodeProfilesResponse(AICodingModel):
    node_id: str
    kind: KindDescriptorResponse
    selected_workflow_profile: WorkflowProfileDescriptorResponse | None = None
    profiles: list[NodeProfileDetailResponse] = Field(default_factory=list)
```

Purpose:

- profile-focused read that is narrower than `node types`

## Suggested Placement In `daemon/models.py`

Recommended insertion area:

- near `NodeKindDefinitionResponse`
- before or near other workflow-inspection response models such as:
  - `CompiledWorkflowResponse`
  - `WorkflowChainResponse`
  - `WorkflowStartResponse`

Reason:

- these new models are inspectable workflow metadata, not runtime mutation results

## Relationship To Existing Models

### Existing `NodeKindDefinitionResponse`

Current shape is too thin for the workflow-overhaul direction.

It currently only expresses:

- kind
- tier
- description
- parent/child kind constraints

Future options:

1. keep it thin and introduce `NodeTypesResponse` as the richer read
2. enrich it directly with profile metadata

Recommended direction:

- keep `NodeKindDefinitionResponse` relatively simple
- add `NodeTypesResponse` as the richer per-node context read

### Existing `WorkflowStartResponse`

This likely remains separate.

Possible future enrichment:

- include selected workflow profile metadata in startup payloads

But do not overload it with the full `workflow brief` payload unless the startup path truly needs that much data.

## Recommended Field Rules

### Rule 1

Use `Field(default_factory=list)` for list fields.

That stays aligned with the existing daemon model style.

### Rule 2

Descriptions should be required for:

- kinds
- profiles
- layouts
- roles

This keeps the user-facing and AI-facing reads interpretable.

### Rule 3

Keep prompt refs optional where the response surface does not always need them.

Example:

- compact profile descriptors may omit prompt refs
- detailed profile rows should include them

### Rule 4

Do not mix:

- recommended child profile subset

with:

- full legal child-profile catalog

Use:

- `WorkflowBriefResponse.recommended_children`

for the subset

and:

- `NodeTypesResponse`
- `NodeProfilesResponse`

for the fuller option surfaces

## Suggested Implementation Sequence

1. add shared descriptor models
2. add `NodeProfilesResponse`
3. add `NodeTypesResponse`
4. add `WorkflowBriefPromptStackResponse` and `WorkflowBriefResponse`
5. wire daemon endpoints
6. wire CLI handlers and parser commands

## Follow-On Notes

After this model draft, the most useful next artifacts would be:

- a draft endpoint inventory note mapping these models to daemon routes
- a pseudo-implementation note for how `daemon/workflows.py` would assemble `WorkflowBriefResponse`
- a pseudo-implementation note for how `daemon/hierarchy.py` and related helpers would assemble `NodeTypesResponse`
