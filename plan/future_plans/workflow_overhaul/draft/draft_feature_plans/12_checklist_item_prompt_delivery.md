# Feature 12: Checklist Item Prompt Delivery

## Goal

Deliver a bounded prompt for one active checklist item, including `When To Use This` and a strict terminal return contract.

## Main Work

- add checklist-item prompt assets
- inject active item context and allowed options
- align prompt contract with daemon-enforced item legality

## Implementation Subtasks

- add the base checklist-item execution prompt assets to the real prompt pack
- inject overarching task context, active item context, allowed options, and terminal return contract fields
- include `When To Use This` and `When Not To Use This` guidance in the active-item prompt contract
- ensure the prompt output schema matches daemon-validated item terminal results

## Main Dependencies

- Setup 01
- Feature 09
- Feature 11

## Flows Touched

- `05_admit_and_execute_node_run_flow`
- future flow `execute_checklist_item`

## Relevant Current Code

- `src/aicoding/resources/prompts/`
- `src/aicoding/operational_library.py`
- `src/aicoding/structural_library.py`
- `src/aicoding/project_policies.py`
- `src/aicoding/daemon/run_orchestration.py`

## Current Gaps

- there are no checklist-item prompt assets in the active prompt pack
- current prompt delivery has no checklist-item return schema, `When To Use This` guidance, or allowed-options rendering
