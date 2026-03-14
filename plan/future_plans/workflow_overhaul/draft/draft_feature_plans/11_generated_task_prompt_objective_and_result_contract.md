# Feature 11: Generated Task Prompt Objective And Result Contract

## Goal

Push template step objectives and provenance into normal generated task prompts and result surfaces without creating a checklist-specific prompt family.

## Main Work

- inject template context into generated task prompts
- align generated-task objectives with normal task-profile prompt packs
- expose generated provenance in result registration and inspection

## Implementation Subtasks

- define the generated-task objective payload delivered to prompts
- surface template id, step id, expected outputs, and proving targets in prompt context
- ensure generated tasks still use normal task result contracts
- prevent template context from creating a second mutation or terminal-result path

## Main Dependencies

- Setup 02
- Feature 09
- Feature 10

## Flows Touched

- `05_admit_and_execute_node_run_flow`
- `06_inspect_state_and_blockers_flow`

## Relevant Current Code

- prompt assets under `src/aicoding/resources/`
- `src/aicoding/daemon/workflows.py`
- `src/aicoding/cli/handlers.py`

## Current Gaps

- there is no prompt contract for generated-task objective context
- the checklist draft assumed a separate prompt family rather than extending normal task prompts
