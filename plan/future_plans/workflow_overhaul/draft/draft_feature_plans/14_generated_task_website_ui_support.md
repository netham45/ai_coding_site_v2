# Feature 14: Generated Task Website UI Support

## Goal

Render template provenance and generated-task grouping in the website UI while keeping browser state aligned with daemon-owned task authority.

## Main Work

- show generated-child grouping
- display template provenance and step lineage
- avoid reimplementing orchestration logic in the browser

## Implementation Subtasks

- add UI detail for template-generated child tasks
- render template id, step title, and dependency lineage where useful
- ensure browser actions still target normal task-level authority surfaces
- verify generated-task views stay consistent across refresh and restart paths

## Main Dependencies

- Setup 02
- Feature 10
- Feature 13

## Flows Touched

- `06_inspect_state_and_blockers_flow`

## Relevant Current Code

- website workflow views under `frontend/src/`
- `frontend/src/lib/api/workflows.js`

## Current Gaps

- there is no website support for template provenance on generated children
- the superseded checklist direction implied checklist-specific browser views rather than task-centric lineage views
