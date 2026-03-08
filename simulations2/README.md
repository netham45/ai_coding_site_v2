# Simulations 2

This folder contains second-pass simulations written as execution ledgers instead of summary sketches.

Each simulation tries to enumerate:

- every CLI command boundary
- every YAML family and file read
- every important daemon-side relation check
- every durable database write
- every lifecycle or run-state transition
- every inspectable follow-up query

These are still simulations, not implemented behavior.

Important limitation:

- several built-in YAML file paths and some event payload shapes are not fully frozen in `notes/`
- where the notes are explicit about a concept but not the exact literal path or payload, the simulation marks that choice as an assumption

## Files

- `01_dependency_blocked_sibling_flow.md`
- `02_invalid_dependency_graph_flow.md`
- `03_parent_child_failure_decision_flow.md`
- `04_child_session_round_trip_flow.md`
- `05_compile_failure_and_reattempt_flow.md`
- `06_resume_after_interruption_flow.md`
- `07_rectification_stateful_flow.md`
