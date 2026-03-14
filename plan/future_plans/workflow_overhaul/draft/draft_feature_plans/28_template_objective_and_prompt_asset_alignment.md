# Feature 28: Template Objective And Prompt Asset Alignment

## Goal

Make the generated-task objective contract executable by defining the runtime prompt assets, injected context, and validation surfaces template-driven generation needs.

## Main Work

- align prompt assets with generated-task objectives
- define template-context injection
- keep prompt behavior consistent with normal task semantics

## Implementation Subtasks

- map template step fields into generated-task prompt rendering
- define the injected provenance payload for generated tasks
- align generated-task prompt context with daemon-enforced task authority
- remove the need for a separate checklist-item prompt family

## Main Dependencies

- Setup 02
- Features 08 through 11

## Flows Touched

- `05_admit_and_execute_node_run_flow`
- `06_inspect_state_and_blockers_flow`

## Relevant Current Code

- prompt assets under `src/aicoding/resources/`
- `src/aicoding/daemon/workflows.py`
- `src/aicoding/cli/handlers.py`

## Current Gaps

- there is no authored prompt-alignment plan for template-driven generated tasks
- the superseded prompt direction is still checklist-item-specific
