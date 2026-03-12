# Feature 28: Checklist Prompt Contract And Prompt Asset Alignment

## Goal

Make the checklist item prompt-contract work executable by defining the runtime prompt assets, injected context, and validation surfaces checklist mode needs.

## Main Work

- align checklist-mode prompt assets with the checklist prompt contract
- make active-item prompt rendering inspectable and reusable
- keep prompt expectations tied to daemon-owned item state and terminal result schemas

## Implementation Subtasks

- define the checklist prompt asset family and composition rules for active-item execution
- align injected context fields with checklist instance data, allowed options, blockers, and terminal return contracts
- define prompt retrieval and inspection surfaces for operators and tests
- document prompt validation expectations so checklist prompts cannot drift from item status and result contracts

## Main Dependencies

- Setup 01
- Feature 12
- Feature 14
- Feature 15
- Feature 25

## Flows Touched

- `05_admit_and_execute_node_run_flow`
- `06_inspect_state_and_blockers_flow`
- `12_query_provenance_and_docs_flow`

## Relevant Current Code

- `src/aicoding/resources/prompts/`
- `src/aicoding/daemon/workflows.py`
- `src/aicoding/cli/handlers.py`
- `frontend/src/components/detail/NodeDetailTabs.js`

## Current Gaps

- the checklist prompt contract existed as a support note, but the draft queue had no standalone execution slice for prompt-asset adoption and alignment
- checklist prompt behavior is currently only planned, not represented in real prompt assets or retrieval surfaces
