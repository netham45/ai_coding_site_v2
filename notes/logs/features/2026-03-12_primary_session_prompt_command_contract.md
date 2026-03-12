# Development Log: Primary Session Prompt Command Contract

## Entry 1

- Timestamp: 2026-03-12T03:45:00-06:00
- Task ID: primary_session_prompt_command_contract
- Task title: Primary session prompt command contract
- Status: started
- Affected systems: CLI, daemon, prompts, notes, tests, development logs
- Summary: Began the implementation pass to make the primary-session prompt retrieval contract self-consistent across durable launch metadata, the bootstrap helper, runtime-generated prompt text, authored prompt assets, and the current authoritative notes.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_primary_session_prompt_command_contract.md`
  - `README.md`
  - `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
  - `notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `notes/specs/cli/cli_surface_spec_v2.md`
  - `notes/specs/prompts/prompt_library_plan.md`
  - `notes/planning/implementation/full_ai_prompt_command_surface_review_note.md`
  - `notes/planning/implementation/ai_cli_bootstrap_and_work_retrieval_commands_decisions.md`
  - `notes/logs/doc_updates/2026-03-12_pythonpath_src_command_docs.md`
- Commands and tests run:
  - `sed -n '1,220p' plan/tasks/2026-03-12_primary_session_prompt_command_contract.md`
  - `sed -n '1,260p' src/aicoding/daemon/session_manager.py`
  - `sed -n '1,240p' src/aicoding/daemon/codex_session_bootstrap.py`
  - `rg -n "subtask prompt --node|PYTHONPATH=src|aicoding.cli.main subtask prompt" tests src notes README.md`
- Result: Confirmed that the launch metadata, bootstrap helper subprocess path, runtime-generated workflow prompts, synthesized command-subtask prompts, and authored execution/layout prompts were still teaching or reconstructing the prompt retrieval command independently.
- Next step: Centralize the prompt command builder, route bootstrap execution through it, patch the prompt/doc drift surfaces, and add bounded proof for the shared command contract.

## Entry 2

- Timestamp: 2026-03-12T04:05:00-06:00
- Task ID: primary_session_prompt_command_contract
- Task title: Primary session prompt command contract
- Status: bounded_tests_passed
- Affected systems: CLI, daemon, prompts, notes, tests, development logs
- Summary: Added a shared repo-local Python module command builder, routed durable prompt metadata and bootstrap subprocess execution through it, updated runtime-generated continuation text plus authored prompt assets to teach the explicit `PYTHONPATH=src` prompt retrieval command, and aligned the authoritative tmux/quickstart/checklist notes with the new contract.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_primary_session_prompt_command_contract.md`
  - `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
  - `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`
  - `plan/checklists/05_tmux_session_and_idle_verification.md`
- Commands and tests run:
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_session_manager.py tests/unit/test_codex_session_bootstrap.py tests/unit/test_prompt_pack.py tests/unit/test_resources.py -q`
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_verification_command_docs.py tests/unit/test_e2e_execution_policy_docs.py tests/unit/test_notes_quickstart_docs.py tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q`
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_workflows.py -q`
- Result: Passed. The bounded proof now pins the shared command text, the bootstrap helper's env/argv contract, the rendered prompt assets, the workflow-rendered continuation strings, and the updated authoritative docs.
- Next step: Run the relevant integration slices that assert session-event payloads still expose the expected prompt command and then stop at implemented-plus-bounded-proof unless a real tmux E2E is added in this batch.

## Entry 3

- Timestamp: 2026-03-12T04:06:00-06:00
- Task ID: primary_session_prompt_command_contract
- Task title: Primary session prompt command contract
- Status: e2e_pending
- Affected systems: CLI, daemon, prompts, notes, tests, development logs
- Summary: Finished the bounded implementation slice and verified the relevant session/event integration surfaces. A broader daemon integration command also exposed a separate live-git conflict API failure that reproduces independently of this prompt-command change and remains out of scope for this batch.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_primary_session_prompt_command_contract.md`
  - `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
  - `plan/checklists/05_tmux_session_and_idle_verification.md`
- Commands and tests run:
  - `PYTHONPATH=src python3 -m pytest tests/integration/test_session_cli_and_daemon.py tests/integration/test_daemon.py -q`
  - `PYTHONPATH=src python3 -m pytest tests/integration/test_daemon.py::test_live_git_conflict_can_be_aborted_via_api -q`
  - `PYTHONPATH=src python3 -m pytest tests/integration/test_session_cli_and_daemon.py::test_session_attach_and_resume_commands_round_trip tests/integration/test_daemon.py::test_session_bind_attach_and_resume_endpoints_work -q`
- Result: The broad integration command failed on `tests/integration/test_daemon.py::test_live_git_conflict_can_be_aborted_via_api`, which still returns an empty `conflicts` list after a real merge-conflict `409`; rerunning that test in isolation reproduced the same unrelated failure. The two relevant session-event integration tests passed and confirmed the prompt command remains present in durable session-event payloads. No real tmux E2E was run in this batch.
- Next step: Add or update a real tmux E2E that proves the taught `PYTHONPATH=src python3 -m aicoding.cli.main subtask prompt --node ...` command is runnable end to end inside the live node-runtime tmux session, and separately triage the existing live-git conflict API failure if broader integration green status is required.
