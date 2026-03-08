# Plan Default Flow

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
- inspect repo and requirements

`generate_child_layout`
- produce `task` children

`review_child_layout`
- ensure the task set covers the prompt

`spawn_children`
- create task nodes

`wait_for_children`
- wait for required tasks

`reconcile_children`
- reset to seed
- merge child finals
- run plan-local reconcile

`validate_node`
- validate merged plan output

`review_node`
- review merged result against plan requirements

`test_node`
- run plan-level testing or accept child evidence if allowed

`update_provenance`
- refresh provenance

`build_node_docs`
- build plan docs

`finalize_node`
- finalize

## Logic issues exposed

1. The built-in leaf `task` flow it depends on now has an explicit execution stage, but the exact default implementation semantics of `execute_node` still need to be fleshed out in the built-in library.
