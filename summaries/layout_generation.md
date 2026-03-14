Generated a two-phase layout in `layouts/generated_layout.yaml`.

- `prerequisite_lane` is the first sibling and has no dependencies.
- `blocked_dependent_lane` is the second sibling and depends only on `prerequisite_lane`.
- The dependency preserves the requested blocked-until-complete ordering without adding extra phases.
