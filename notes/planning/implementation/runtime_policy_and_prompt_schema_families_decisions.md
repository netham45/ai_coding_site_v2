# Runtime Policy And Prompt Schema Family Decisions

## Phase

- `plan/features/45_F04_runtime_policy_and_prompt_schema_families.md`

## Decision Summary

- `runtime_definition`, `runtime_policy_definition`, and `prompt_reference_definition` are now treated as rigid schema families instead of lightweight typed blobs.
- Validation now checks real asset linkage:
  - runtime actions must point at packaged built-in subtasks
  - runtime-policy refs must point at packaged runtime, hook, review, testing, and docs YAML assets
  - prompt-reference docs must point at packaged markdown prompt assets

## Boundary Clarification

- This phase does not add a new prompt placeholder declaration file format.
- Placeholder/render behavior remains code-owned through the existing compiler render-context model.
- The schema layer now validates prompt-linked references and asset targets, but not an additional prompt-authored rendering algorithm.

## Testing Expectations Frozen By This Phase

- invalid runtime definitions must fail early on empty commands, actions, or thresholds
- invalid runtime-policy refs must fail during YAML validation rather than later in policy resolution
- invalid prompt-reference keys or missing prompt targets must fail during YAML validation
