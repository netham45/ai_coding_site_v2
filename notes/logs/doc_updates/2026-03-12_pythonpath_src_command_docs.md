# PYTHONPATH In Command Docs

## Entry 1

- Timestamp: 2026-03-12T03:12:00-06:00
- Task ID: pythonpath_src_command_docs
- Task title: PYTHONPATH in command docs
- Status: started
- Affected systems: CLI, daemon, notes, tests
- Summary: Began normalizing the current authoritative Python command docs so checkout-local `python3 -m ...` examples explicitly include `PYTHONPATH=src`. Scoped the change to the active command-document surfaces rather than every historical plan note.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_pythonpath_src_command_docs.md`
  - `README.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`
- Commands and tests run:
  - `rg -n "python3 -m (aicoding|pytest)" README.md notes plan tests/unit`
  - `sed -n '1,220p' tests/unit/test_verification_command_docs.py`
  - `sed -n '1,220p' tests/unit/test_e2e_execution_policy_docs.py`
  - `sed -n '1,140p' notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`
- Result: Confirmed the authoritative command surfaces currently using raw `python3 -m ...` examples are the root README, the verification command catalog, the E2E execution policy, and the getting-started walkthrough, with bounded tests pinning part of that text.
- Next step: Update those docs and the bounded doc tests, then rerun the targeted verification suite.

## Entry 2

- Timestamp: 2026-03-12T03:19:00-06:00
- Task ID: pythonpath_src_command_docs
- Task title: PYTHONPATH in command docs
- Status: complete
- Affected systems: CLI, daemon, notes, tests
- Summary: Updated the current authoritative Python command docs to use `PYTHONPATH=src` for checkout-local module execution and aligned the bounded documentation tests with the new command form.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_pythonpath_src_command_docs.md`
  - `README.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`
- Commands and tests run:
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_verification_command_docs.py tests/unit/test_e2e_execution_policy_docs.py tests/unit/test_notes_quickstart_docs.py -q`
- Result: Passed. The authoritative command docs now consistently show the explicit local import-path posture. Historical plan/task notes were intentionally left out of scope for this normalization pass.
- Next step: If you want the same normalization applied across older task plans and future-plan docs too, do that as a separate broader doc-cleanup batch.
