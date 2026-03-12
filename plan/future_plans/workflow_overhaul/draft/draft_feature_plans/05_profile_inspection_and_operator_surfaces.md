# Feature 05: Profile Inspection And Operator Surfaces

## Goal

Expose profile-aware read surfaces such as `node types`, `node profiles`, and `workflow brief`.

## Main Work

- add daemon/API profile inspection routes
- add CLI handlers and parser entries
- keep thin vs rich operator surfaces distinct

## Implementation Subtasks

- add daemon routes for `node types`, `node profiles`, and `workflow brief`
- define response models that keep `node kinds` thin and richer node-context reads separate
- add CLI parser entries and handlers for the new inspection commands
- implement shared helper logic so all profile-aware reads derive from one runtime source of truth

## Main Dependencies

- Setup 02
- Feature 04

## Flows Touched

- `06_inspect_state_and_blockers_flow`
- `12_query_provenance_and_docs_flow` for inspection-surface consistency

## Relevant Current Code

- `src/aicoding/daemon/app.py`
- `src/aicoding/cli/parser.py`
- `src/aicoding/cli/handlers.py`
- `src/aicoding/daemon/operator_views.py`
- `frontend/src/lib/api/types.js`
- `frontend/src/lib/api/workflows.js`

## Current Gaps

- there are no daemon or CLI routes for `node profiles`, rich `node types`, or `workflow brief`
- website API surfaces currently expose current workflow/subtask data, not profile-aware inspection data
