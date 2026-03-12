# Reset DB Script

## Entry 1

- Timestamp: 2026-03-12T02:38:00-06:00
- Task ID: reset_db_script
- Task title: Reset DB script
- Status: started
- Affected systems: database, CLI, notes, tests
- Summary: Began adding a guarded root shell wrapper for fully resetting the configured PostgreSQL database. Reviewed the documented bootstrap commands and the existing database reset helper so the script can wipe the configured DB safely and then replay the repository's documented rebuild path.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_reset_db_script.md`
  - `README.md`
  - `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `notes/planning/implementation/setup_bootstrap_decisions.md`
  - `notes/logs/features/2026-03-11_yaml_schema_and_field_rigidity_implementation.md`
- Commands and tests run:
  - `sed -n '1,220p' README.md`
  - `sed -n '1,220p' src/aicoding/db/bootstrap.py`
  - `sed -n '1110,1165p' src/aicoding/cli/parser.py`
  - `sed -n '60,150p' src/aicoding/cli/handlers.py`
- Result: Confirmed that the repo already provides the canonical rebuild commands (`admin db ping`, `admin db heads`, `admin db upgrade`, `admin db check-schema`) and a safer `reset_public_schema()` helper that preserves `public` instead of dropping and recreating it.
- Next step: Add `scripts/reset-db.sh`, update the root command docs, extend the bounded script-surface test, and run the targeted verification suite.

## Entry 2

- Timestamp: 2026-03-12T02:49:00-06:00
- Task ID: reset_db_script
- Task title: Reset DB script
- Status: complete
- Affected systems: database, CLI, notes, tests
- Summary: Added the guarded `scripts/reset-db.sh` wrapper, documented it in the repo command surfaces, and extended bounded script-surface verification to cover the new destructive entrypoint.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_reset_db_script.md`
  - `README.md`
  - `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `notes/planning/implementation/setup_bootstrap_decisions.md`
- Commands and tests run:
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_scripts_surface.py tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py tests/unit/test_verification_command_docs.py -q`
- Result: Passed. The new script now wipes the configured DB through the repo helper, then reruns the documented bootstrap commands. Verification remains bounded-layer only; the destructive script itself was not executed against the live configured database during this task.
- Next step: Use `./scripts/reset-db.sh --yes` when you want to wipe and rebuild the configured local database, and keep the wrapper aligned if the documented bootstrap command family changes later.
