# Feature 06: Prompt Pack And Prompt Selection Adoption

## Goal

Promote the workflow-overhaul prompt bundle into a real prompt-selection model once profile/runtime contracts are stable.

## Main Work

- adopt base plus overlay prompt assets
- normalize prompt references
- make prompt-stack composition inspectable

## Implementation Subtasks

- choose the real prompt-pack directory layout for base prompts, overlays, and briefing prompts
- normalize prompt reference naming across schema, compile logic, and builtin assets
- move the selected workflow-overhaul prompt assets into real runtime-owned prompt locations
- expose prompt-stack composition and selected prompt refs through compiled inspection surfaces

## Main Dependencies

- Setup 01
- Feature 04
- Feature 05

## Flows Touched

- `02_compile_or_recompile_workflow_flow`
- `05_admit_and_execute_node_run_flow`

## Relevant Current Code

- `src/aicoding/operational_library.py`
- `src/aicoding/quality_library.py`
- `src/aicoding/structural_library.py`
- `src/aicoding/project_policies.py`
- `src/aicoding/source_lineage.py`
- `src/aicoding/resources/yaml/builtin/system-yaml/prompts/default_prompt_refs.yaml`

## Current Gaps

- prompt selection is still based on existing prompt-pack references, with no workflow-profile base-plus-overlay composition
- current runtime has no inspectable prompt-stack composition surface tied to compiled workflow state
