# Project Bootstrap Flow

Sources:

- `notes/yaml_inventory_v2.md`
- `notes/yaml_schemas_spec_v2.md`
- `notes/override_versioning_note.md`

## Scenario

A new repository is added to the system with project-local policy and overrides.

## Full task flow

### Step 1: create local `.ai/` structure

Expected families:

- policies
- testing
- docs
- overrides

### Step 2: author project-local YAML

- `project_policy_definition`
- `testing_definition`
- `documentation_definition`
- override docs with compatibility metadata

### Step 3: validate local YAML

```text
ai-tool yaml validate --path .ai/policies/project.yaml
ai-tool yaml validate --path .ai/testing/python_default.yaml
ai-tool yaml validate --path .ai/overrides/nodes/plan.yaml
```

### Step 4: create first node in the project

This triggers:

- source discovery
- override compatibility checks
- workflow compilation

### Step 5: inspect resolved workflow

```text
ai-tool workflow show --node proj_plan_v1
ai-tool yaml resolved --node proj_plan_v1
```

## Logic issues exposed

1. The notes still do not define one canonical high-level “add project” command.
2. Override compatibility warning versus hard-failure thresholds are still not fully frozen.

