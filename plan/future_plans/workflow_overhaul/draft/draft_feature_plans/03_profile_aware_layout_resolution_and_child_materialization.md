# Feature 03: Profile-Aware Layout Resolution And Child Materialization

## Goal

Resolve effective layouts from selected profiles and materialize children with profile-aware role and child-profile expectations.

## Main Work

- resolve default layout from selected profile
- validate explicit/generated layout precedence
- expose child role/profile metadata during materialization
- enforce child-materialization prerequisites for non-leaf advancement

## Implementation Subtasks

- implement effective layout resolution from selected profile plus explicit/generated overrides
- validate layout compatibility with the selected profile before child materialization proceeds
- include child role and recommended child-profile metadata in materialization outputs and inspection surfaces
- enforce non-leaf blocked mutation behavior when required children are missing or role coverage is incomplete

## Main Dependencies

- Setup 01
- Setup 02
- Feature 01
- Feature 02

## Flows Touched

- `03_materialize_and_schedule_children_flow`
- `04_manual_tree_edit_and_reconcile_flow`

## Relevant Current Code

- `src/aicoding/daemon/materialization.py`
- `src/aicoding/daemon/app.py`
- `src/aicoding/daemon/interventions.py`
- `src/aicoding/daemon/actions.py`
- `src/aicoding/cli/parser.py`
- `src/aicoding/cli/handlers.py`
- `tests/unit/test_materialization.py`
- `tests/e2e/test_flow_03_materialize_and_schedule_children_real.py`

## Current Gaps

- materialization currently resolves layouts without any workflow-profile-aware precedence or role coverage logic
- non-leaf blocked advancement is not enforced from profile-derived child-role obligations
