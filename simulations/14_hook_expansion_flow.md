# Hook Expansion Flow

Source:

- `notes/hook_expansion_algorithm.md`

## Scenario

A built-in `before_review` hook and a project extension hook both apply.

## Full task flow

1. collect candidate hooks
2. filter by insertion point
3. filter by context
4. order deterministically
5. compile hook run units
6. insert into workflow
7. validate expanded workflow

Original review stage:

1. `build_context`
2. `review`
3. `write_summary`

Expanded stage:

1. `build_context`
2. built-in pre-review hook unit
3. project pre-review hook unit
4. `review`
5. `write_summary`

## Logic issues exposed

1. Duplicate semantic-stage handling is still only partly formalized; the current rule is mostly “fail if dangerous”.

