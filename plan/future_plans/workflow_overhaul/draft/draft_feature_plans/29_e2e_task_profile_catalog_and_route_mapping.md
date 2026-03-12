# Feature 29: E2E Task Profile Catalog And Route Mapping

## Goal

Turn the E2E task-profile catalog into explicit executable work for task-profile definition, route mapping, and E2E traceability.

## Main Work

- define how `task.e2e.*` profiles fit into the workflow-profile family
- align route plans, profile catalogs, and proving ownership
- prevent E2E task profiles from remaining note-only ideas

## Implementation Subtasks

- define the authoritative catalog shape for E2E-oriented task profiles and their intended role in the workflow-profile family
- map each E2E task-profile family member to the route plans and proving slices that are expected to cover it
- align startup, inspection, and prompt expectations for E2E task profiles with the broader workflow-profile runtime contract
- document residual open questions for E2E profile granularity so later implementation does not improvise the catalog

## Main Dependencies

- Setup 01
- Setup 03
- Feature 01
- Feature 02
- Feature 07

## Flows Touched

- `01_create_top_level_node_flow`
- `05_admit_and_execute_node_run_flow`
- `09_run_quality_gates_flow`
- `12_query_provenance_and_docs_flow`

## Relevant Current Code

- `plan/future_plans/workflow_overhaul/e2e_task_profiles/`
- `plan/future_plans/workflow_overhaul/draft/e2e_route_plans/`
- `plan/future_plans/workflow_overhaul/draft/e2e_route_subplans/`
- `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`

## Current Gaps

- the E2E task-profile catalog existed as a support note, but the draft queue had no standalone execution slice for making that catalog implementation-facing
- route coverage and E2E profile identity were still coupled only indirectly through support notes and examples
