# Development Log: Tmux Session Cleanup Lifecycle Review

## Entry 1

- Timestamp: 2026-03-12T10:35:00-06:00
- Task ID: tmux_session_cleanup_lifecycle_review
- Task title: Review tmux/Codex session cleanup lifecycle and test leak posture
- Status: started
- Affected systems: CLI, daemon, tests, notes, development logs
- Summary: Began a review of when daemon-managed tmux/Codex sessions should stay alive versus be cleaned up, with special focus on the real E2E harness and the repeated leaked-session reports during tmux-backed testing.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_tmux_session_cleanup_lifecycle_review.md`
  - `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
  - `notes/contracts/runtime/session_recovery_appendix.md`
  - `plan/features/16_F12_session_binding_and_resume.md`
  - `plan/features/39_F12_tmux_session_manager.md`
  - `plan/checklists/05_tmux_session_and_idle_verification.md`
  - `tests/fixtures/e2e.py`
  - `tests/helpers/e2e.py`
  - `tests/e2e/test_tmux_codex_idle_nudge_real.py`
  - `src/aicoding/daemon/session_manager.py`
  - `src/aicoding/daemon/session_records.py`
- Commands and tests run:
  - `rg -n "tmux|session|kill-session|cleanup|remain-on-exit|supervis" notes src tests -S`
  - `sed -n '1,320p' notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
  - `sed -n '1,360p' tests/helpers/e2e.py`
  - `sed -n '1,260p' tests/fixtures/e2e.py`
  - `sed -n '1,260p' tests/e2e/test_tmux_codex_idle_nudge_real.py`
  - `sed -n '1,320p' src/aicoding/daemon/session_manager.py`
  - `sed -n '1,360p' src/aicoding/daemon/session_records.py`
- Result: Confirmed that the authoritative tmux lifecycle note covered bind, recovery, and lost-session semantics but did not yet state a strong terminal/replacement cleanup policy, and that the real E2E harness terminated the daemon and dropped the test database without centrally killing the tmux sessions recorded by that harness.
- Next step: Add explicit cleanup doctrine to the tmux lifecycle note, centralize harness-owned tmux cleanup for real E2E teardown, and run the affected bounded/document checks.

## Entry 2

- Timestamp: 2026-03-12T10:35:00-06:00
- Task ID: tmux_session_cleanup_lifecycle_review
- Task title: Review tmux/Codex session cleanup lifecycle and test leak posture
- Status: complete
- Affected systems: CLI, daemon, tests, notes, development logs
- Summary: Added explicit tmux cleanup doctrine for terminal, replaced, superseded, and paused sessions in the authoritative lifecycle note and made the real E2E harness kill the tmux sessions durably recorded in its own test database during teardown so leaked sessions no longer depend on every test file remembering manual cleanup.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_tmux_session_cleanup_lifecycle_review.md`
  - `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
  - `notes/contracts/runtime/session_recovery_appendix.md`
  - `plan/features/16_F12_session_binding_and_resume.md`
  - `plan/features/39_F12_tmux_session_manager.md`
  - `plan/checklists/05_tmux_session_and_idle_verification.md`
  - `tests/helpers/e2e.py`
  - `tests/unit/test_e2e_harness.py`
- Commands and tests run:
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_e2e_harness.py tests/unit/test_document_schema_docs.py -q`
- Result: Passed. The repo now has an explicit answer for when tmux sessions should remain alive versus be cleaned up, and the real E2E harness has a central teardown path that kills the tmux sessions recorded for its isolated database instead of relying solely on ad hoc per-test cleanup loops.
- Next step: Fold the same lifecycle policy into daemon-owned runtime cleanup paths so terminal, replaced, and superseded sessions are cleaned automatically outside the test harness as well.
