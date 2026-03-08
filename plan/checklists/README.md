# Checklist Phases

These phases are verification phases.

They are not optional clean-up.

They ensure:

- all required database structures exist
- database schema families are verified separately when runtime state and history/audit concerns diverge
- all required CLI commands exist
- all required YAML, prompt, and workflow assets exist
- test coverage is exhaustive
- design assumptions hold across every stage
- stack and performance assumptions are verified explicitly, not inferred

Run these after setup and feature phases, and rerun them whenever major features land.
