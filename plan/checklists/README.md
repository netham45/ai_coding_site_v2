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

Document-schema references:

- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`

Canonical status/command references:

- `notes/catalogs/checklists/feature_checklist_standard.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
