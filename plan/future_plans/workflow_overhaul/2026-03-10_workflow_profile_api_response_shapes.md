# Workflow Profile API Response Shapes

## Purpose

Define draft daemon/API response shapes for the workflow-profile-aware inspection surfaces proposed in this workflow-overhaul bundle.

This note is a working draft.

It is not an adopted API contract.

## Covered Surfaces

This note covers the likely future response shapes for:

- `workflow brief --node <id>`
- `node types --node <id>`
- `node profiles --node <id>`

These are the three most important inspection surfaces for making workflow profiles understandable to operators and AI contributors.

## Design Rules

### Rule 1

Return descriptions, not ids only.

Any response that lists:

- kinds
- profiles
- layouts
- child roles

should include human-readable descriptions alongside ids.

### Rule 2

Separate:

- recommended subset

from:

- full legal option set

The brief should show the recommendation.

The type/profile surfaces should show the broader legal space.

### Rule 3

Expose the prompt stack without forcing callers to inspect raw prompt files manually.

The future responses should surface:

- node-tier prompt reference
- profile prompt reference
- brief-generation posture

### Rule 4

Keep the brief operator-facing and compact.

The `node types` and `node profiles` surfaces can be fuller and more catalog-like.

### Rule 5

Inspection surfaces must expose enforcement state, not only recommendations.

The future responses should make it possible to see:

- whether the current profile is decomposition-required
- which step is currently legal
- which completion restrictions remain active
- why merge, finalize, or completion would currently be blocked

## Draft `workflow brief` Response

### Purpose

Tell the caller:

- what this node is trying to do
- which workflow profile is currently in effect
- which child profiles are recommended
- how to inspect the full option set if the recommendation is not enough

### Suggested shape

```json
{
  "node_id": "7c2d...",
  "kind": {
    "id": "epic",
    "name": "Epic",
    "description": "Top-level outcome-oriented planning container."
  },
  "workflow_profile": {
    "id": "epic.feature",
    "name": "Feature Epic",
    "description": "Deliver a feature through discovery, implementation, docs alignment, and real proof."
  },
  "objective": "Deliver the feature through discovery, implementation, docs alignment, and real proof.",
  "prompt_stack": {
    "node_tier_prompt_ref": "prompts/layouts/generate_phase_layout.md",
    "workflow_profile_prompt_ref": "prompts/epic/feature.md",
    "brief_prompt_ref": "prompts/epic/global_brief.md"
  },
  "selected_layout": {
    "id": "epic_feature_to_phases",
    "name": "Feature Epic To Phases",
    "description": "Standard feature-delivery epic breakdown."
  },
  "recommended_children": [
    {
      "role": "discovery",
      "description": "Clarify scope, invariants, risks, and implementation boundaries.",
      "workflow_profile": {
        "id": "phase.discovery",
        "name": "Discovery Phase",
        "description": "Clarify scope, invariants, risks, and implementation boundaries before execution."
      }
    },
    {
      "role": "documentation",
      "description": "Align notes, commands, and checklists with implemented behavior.",
      "workflow_profile": {
        "id": "phase.documentation",
        "name": "Documentation Phase",
        "description": "Align notes, commands, checklists, and process docs with implemented behavior."
      }
    }
  ],
  "required_repository_updates": [
    "notes",
    "checklist",
    "development_log"
  ],
  "required_verification": [
    "bounded_tests",
    "real_e2e"
  ],
  "enforcement": {
    "decomposition_required": true,
    "required_step_sequence": [
      "compile",
      "spawn_children",
      "wait_for_children",
      "merge_children",
      "complete"
    ],
    "blocked_actions": [
      {
        "action": "complete",
        "code": "children_required_before_completion",
        "message": "you did not spawn children before attempting merge or completion"
      }
    ]
  },
  "cli_discovery_note": {
    "summary": "Use node types or node profiles to inspect the full available child-profile set beyond the recommended defaults.",
    "commands": [
      "node types --node 7c2d...",
      "node profiles --node 7c2d..."
    ]
  }
}
```

### Required fields

- `node_id`
- `kind`
- `workflow_profile`
- `objective`
- `prompt_stack`
- `recommended_children`
- `cli_discovery_note`

### Notes

- `objective` should be a concise generated statement, not only a raw prompt ref
- `recommended_children` should be the recommended subset, not the full legal catalog
- the brief should expose blocked-step reasons compactly when the current node is not yet legally completable

## Draft `node types` Response

### Purpose

Tell the caller:

- what kind of node this is
- what profiles and layouts are legal from here
- what child roles and kinds are structurally allowed

### Suggested shape

```json
{
  "node_id": "7c2d...",
  "kind": {
    "id": "epic",
    "name": "Epic",
    "description": "Top-level outcome-oriented planning container."
  },
  "selected_workflow_profile": {
    "id": "epic.feature",
    "name": "Feature Epic",
    "description": "Deliver a feature through discovery, implementation, docs alignment, and real proof."
  },
  "default_workflow_profile": {
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
    },
    {
      "id": "epic.review",
      "name": "Review Epic",
      "description": "Inspect an existing system, remediate issues, and confirm the remediation."
    }
  ],
  "compatible_layouts": [
    {
      "id": "epic_feature_to_phases",
      "name": "Feature Epic To Phases",
      "description": "Standard feature-delivery epic breakdown."
    },
    {
      "id": "epic_planning_to_phases",
      "name": "Planning Epic To Phases",
      "description": "Planning-oriented epic breakdown for requirements, architecture, planning, and verification mapping."
    }
  ],
  "allowed_child_kinds": [
    {
      "id": "phase",
      "description": "Execution slice inside one delivery band."
    }
  ],
  "child_roles": [
    {
      "role": "discovery",
      "description": "Clarify scope, invariants, risks, and implementation boundaries.",
      "recommended_workflow_profile": {
        "id": "phase.discovery",
        "name": "Discovery Phase",
        "description": "Clarify scope, invariants, risks, and implementation boundaries before execution."
      }
    },
    {
      "role": "e2e",
      "description": "Prove the intended flow through real runtime boundaries.",
      "recommended_workflow_profile": {
        "id": "phase.e2e",
        "name": "E2E Phase",
        "description": "Prove the intended flow through the real runtime boundaries and capture the resulting status honestly."
      }
    }
  ]
}
```

### Required fields

- `node_id`
- `kind`
- `supported_workflow_profiles`
- `compatible_layouts`
- `allowed_child_kinds`
- `child_roles`

### Notes

- `node types` is the broader structural/type catalog
- it should be sufficient for callers that need to go beyond the brief recommendation

## Draft `node profiles` Response

### Purpose

Give a profile-focused read when the caller cares about profile options more than structural kinds.

### Suggested shape

```json
{
  "node_id": "7c2d...",
  "kind": {
    "id": "epic",
    "description": "Top-level outcome-oriented planning container."
  },
  "selected_workflow_profile": {
    "id": "epic.feature",
    "name": "Feature Epic",
    "description": "Deliver a feature through discovery, implementation, docs alignment, and real proof.",
    "main_prompt_ref": "prompts/epic/feature.md",
    "default_child_layout": "layouts/epic_feature_to_phases.yaml"
  },
  "profiles": [
    {
      "id": "epic.planning",
      "name": "Planning Epic",
      "description": "Turn rough intent into explicit requirements, architecture, and verification mapping.",
      "main_prompt_ref": "prompts/epic/planning.md",
      "default_child_layout": "layouts/epic_planning_to_phases.yaml",
      "required_child_roles": [
        {
          "role": "requirements",
          "description": "Clarify the product request, boundaries, and invariants."
        },
        {
          "role": "verification_mapping",
          "description": "Define the proving commands and E2E target for the planned scope."
        }
      ]
    },
    {
      "id": "epic.feature",
      "name": "Feature Epic",
      "description": "Deliver a feature through discovery, implementation, docs alignment, and real proof.",
      "main_prompt_ref": "prompts/epic/feature.md",
      "default_child_layout": "layouts/epic_feature_to_phases.yaml",
      "required_child_roles": [
        {
          "role": "discovery",
          "description": "Clarify scope, invariants, risks, and implementation boundaries."
        },
        {
          "role": "documentation",
          "description": "Align notes, commands, and checklists with implemented behavior."
        }
      ]
    }
  ]
}
```

### Required fields

- `node_id`
- `kind`
- `profiles`

### Notes

- this surface is narrower than `node types`
- it should still include descriptions and prompt/layout references, not only ids

## Proposed Shared Nested Shapes

### `KindDescriptor`

```json
{
  "id": "epic",
  "name": "Epic",
  "description": "Top-level outcome-oriented planning container."
}
```

### `WorkflowProfileDescriptor`

```json
{
  "id": "epic.feature",
  "name": "Feature Epic",
  "description": "Deliver a feature through discovery, implementation, docs alignment, and real proof.",
  "main_prompt_ref": "prompts/epic/feature.md",
  "default_child_layout": "layouts/epic_feature_to_phases.yaml"
}
```

### `LayoutDescriptor`

```json
{
  "id": "epic_feature_to_phases",
  "name": "Feature Epic To Phases",
  "description": "Standard feature-delivery epic breakdown."
}
```

### `RoleDescriptor`

```json
{
  "role": "documentation",
  "description": "Align notes, commands, and checklists with implemented behavior."
}
```

## Proposed Backend Mapping

If these surfaces are implemented, likely daemon models would include:

- `WorkflowBriefResponse`
- `NodeTypesResponse`
- `NodeProfilesResponse`
- shared descriptors for:
  - kind
  - workflow profile
  - layout
  - child role

This would keep the future CLI handlers thin and avoid duplicating shape logic in the CLI layer.

## Suggested Implementation Order

1. adopt shared descriptor models
2. implement `node profiles`
3. implement `node types`
4. implement `workflow brief`

Reason:

- `node profiles` is the smallest slice
- `node types` adds layout and role surfaces
- `workflow brief` depends on the recommendation logic and prompt-stack composition
