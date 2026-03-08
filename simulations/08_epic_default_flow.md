# Epic Default Flow

Source:

- `notes/default_yaml_library_plan.md`

## Proposed task sequence

1. `research_context`
2. `generate_child_layout`
3. `review_child_layout`
4. `spawn_children`
5. `wait_for_children`
6. `reconcile_children`
7. `validate_node`
8. `review_node`
9. `test_node`
10. `update_provenance`
11. `build_node_docs`
12. `finalize_node`

## Full task transcript

`research_context`
- gather epic requirements
- possibly push bounded research child sessions
- summarize scope

`generate_child_layout`
- create `phase` children
- define dependencies and acceptance criteria

`review_child_layout`
- review decomposition against the epic prompt

`spawn_children`
- materialize phase children
- create edges and compile child workflows

`wait_for_children`
- wait until all required phases are complete
- route child failure into parent decision logic

`reconcile_children`
- reset epic branch to seed
- merge child finals
- run epic-local reconcile

`validate_node`
- structural/output validation

`review_node`
- semantic review

`test_node`
- run epic-scoped tests if applicable

`update_provenance`
- refresh provenance

`build_node_docs`
- build docs

`finalize_node`
- record final git state and complete

## Logic issues exposed

1. There is no explicit place in this default sequence for hybrid manual/layout tree reconciliation, even though the notes now make that a first-class concern.
