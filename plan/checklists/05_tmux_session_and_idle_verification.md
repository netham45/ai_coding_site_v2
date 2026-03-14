# Checklist C05: tmux, Session, And Idle Verification

## Goal

Verify that tmux-backed session management, screen polling, idle detection, and recovery behave as designed.

## Verify

- tmux sessions are created and named deterministically
- session records match tmux-backed reality
- idle detection uses the intended polling/classifier behavior
- nudges, pause paths, and recovery paths are all durable and inspectable

## Tests

- exhaustive tmux/session/idle/recovery tests
- performance checks for polling overhead and recovery latency

## Notes

- update session, recovery, and idle notes if the implemented mechanics differ from assumptions

## Discovered Issues

- 2026-03-10: The live primary-session tmux launch path is now Codex-backed for fresh bind and provider-agnostic recovery, but there is not yet dedicated real E2E proof for primary-session Codex launch, idle, nudge, repeated-idle, and live completion/failure behavior.
- 2026-03-10: Child-session launch still uses the long-lived interactive shell launch plan, so child-session tmux/Codex proof remains a separate gap from the primary-session runtime path.
- 2026-03-10: The first real primary-session launch E2E passes only when it asserts on the pane process command line rather than `pane_current_command`; the tmux pane command name is too weak a signal because the Codex path includes a bootstrap helper and the installed `codex` entrypoint is Node-based.
- 2026-03-10: The prompt-bootstrap E2E currently fails because the bound primary tmux session may exit before the recorded `prompt_log_path` is written, which blocks the intended idle/nudge/repeated-idle runtime narrative.
- 2026-03-11: The daemon now has a background supervision loop that automatically replaces a killed tracked primary tmux session, with bounded proof plus passing real tmux Flow 07 proof for the autonomous replacement path.
- 2026-03-11: The unrecoverable replacement-failure branch is covered in bounded fake-backed integration tests, but there is not yet a stable passing real tmux E2E that proves the unfinished run becomes `FAILED` when replacement cannot be created in the real environment.
- 2026-03-12: Primary-session launch and replacement now prefer the authoritative node runtime repo as the execution cwd when a live node repo exists, but there is not yet dedicated real tmux proof that fresh bind and replacement both stay rooted in that node-runtime cwd across the current repo-backed narratives.
- 2026-03-12: Fresh bootstrap and next-stage prompt retrieval now use an explicit `PYTHONPATH=src python3 -m aicoding.cli.main subtask prompt --node ...` contract in bounded code, prompt, and note proof, but there is not yet dedicated real tmux proof that this exact taught command remains runnable end to end inside the live node-runtime tmux session.
- 2026-03-12: After a supervision-caused terminal failure, bounded and integration proof now keep `session show`, `node run show`, `subtask current`, and `node recovery-status` inspectable through the latest failed run/session snapshot, but there is not yet dedicated real tmux E2E proof for that same failed-run inspection behavior after an actual tmux-loss recovery failure.
- 2026-03-12: Primary tmux sessions now preserve dead panes with `remain-on-exit` and expose `tmux_process_alive` plus `tmux_exit_status` in bounded and integration proof. Real tmux E2E now confirms the preserved-dead inspection behavior, but it still fails because the live bootstrap command dies in the node runtime repo with `ModuleNotFoundError: No module named 'aicoding'`, so the remaining blocker has shifted from disappearing tmux sessions to the repo-local bootstrap import contract.
- 2026-03-12: The daemon now pre-seeds a session-owned Codex `config.toml` plus explicit `codex -C <cwd>` launch path for fresh/recovery primary sessions, but the real tmux E2E layer still needs proof that this provider-side trust preapproval actually suppresses the startup prompt in the live environment instead of relying on the runtime trust-handler fallback.
- 2026-03-12: Real tmux proof now shows the provider-side trust preseed removes the startup trust prompt and keeps the original primary session alive, but the idle/nudge E2E still fails because the live Codex session emits pre-nudge chatter and the run pauses instead of completing after the daemon reminder. The remaining blocker is no longer startup or trust-gate loss; it is prompt-compliance/runtime-behavior drift in the live Codex session.
- 2026-03-12: Daemon-owned tmux cleanup now has bounded and fake-backed CLI/daemon proof plus passing real tmux E2E proof for replacement cleanup, terminal run cleanup, superseded-version cleanup, and delegated child-session cleanup across the named Flow 07, idle/nudge, and Flow 21 runtime narratives.
