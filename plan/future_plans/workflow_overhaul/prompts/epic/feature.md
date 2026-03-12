Overlay Role Delta
- Use with `epic/base.md`.
- This overlay turns the epic into a feature-delivery root.
- Keep implementation, documentation alignment, and real proving structurally visible.

Overlay Objective Delta
- Decompose the feature effort into the minimum coherent set of phases needed to reach real proof.

Profile-Specific Inputs
- `required_child_roles` should usually include:
  - `discovery`
  - `implementation`
  - `documentation`
  - `e2e`

Additional Forbidden Actions
- Do not stop at bounded proof only.
- Do not omit the documentation-alignment band.
- Do not create overlapping or decorative phases.
- Do not replace missing child bands by performing their implementation work at the epic tier.

Profile-Specific Expected Result
- A phase child set whose usual roles include:
  - `discovery`
  - `implementation`
  - `documentation`
  - `e2e`

Profile-Specific Completion Conditions
- The child set covers the required delivery bands for feature work.
- Each phase has a distinct contract, expected outputs, and verification posture.
- Notes, checklist, and E2E obligations remain visible in the structure.
