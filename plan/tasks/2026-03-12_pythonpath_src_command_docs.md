# Task: PYTHONPATH In Command Docs

## Goal

Update the current authoritative Python command-document surfaces so local command examples consistently include `PYTHONPATH=src` where they invoke the repository's Python modules directly from the checkout.

## Rationale

- Rationale: The repository currently documents many Python commands in canonical docs, but the command text is inconsistent about whether it makes the local `src/` import path explicit.
- Reason for existence: This task exists to normalize the current authoritative command docs around one explicit local-shell posture without rewriting every historical plan note that contains an older inline example.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/44_F04_validation_review_testing_docs_rectification_schema_families.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`

## Scope

- Database: not affected beyond the documented invocation posture for existing CLI commands.
- CLI: no implementation change; only the documented invocation form changes.
- Daemon: no implementation change; only the documented invocation form changes.
- YAML: not affected in this slice.
- Prompts: not affected in this slice.
- Tests: update bounded documentation tests that assert the old command text.
- Performance: not affected.
- Notes: update the current authoritative command docs and keep their test expectations aligned.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_verification_command_docs.py tests/unit/test_e2e_execution_policy_docs.py tests/unit/test_notes_quickstart_docs.py -q
```

## Exit Criteria

- the current authoritative Python command docs use `PYTHONPATH=src` consistently for checkout-local module execution
- bounded doc tests are updated to expect the new command form
- no claim is made that historical plan/task notes were exhaustively normalized in this slice
