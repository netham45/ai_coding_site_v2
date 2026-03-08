# Task Default Flow

Source:

- `notes/default_yaml_library_plan.md`

## Proposed task sequence

1. `research_context`
2. `execute_node`
3. `validate_node`
4. `review_node`
5. `test_node`
6. `update_provenance`
7. `build_node_docs`
8. `finalize_node`

## Full task transcript

`research_context`
- inspect target files
- build execution context

`execute_node`
- perform the leaf node's implementation or other primary work

`validate_node`
- run required checks

`review_node`
- review output

`test_node`
- run tests

`update_provenance`
- update provenance

`build_node_docs`
- build docs

`finalize_node`
- finalize

## Logic issues exposed

1. The built-in flow now has an explicit implementation stage, but the built-in `execute_node` task still needs a concrete default task definition.
