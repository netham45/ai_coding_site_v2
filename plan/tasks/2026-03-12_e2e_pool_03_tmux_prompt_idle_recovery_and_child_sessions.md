# Task: E2E Pool 03 Tmux Prompt Idle Recovery And Child Sessions

## Goal

Fix the tmux/provider session lifecycle defects that break prompt delivery, idle-nudge flows, supervision restart, human gates, and child-session merge-back.

## Rationale

- These failures share the same session-management surface even when the user-visible symptom differs.
- They can be repaired in parallel with the bind/decomposition pools.
- Rationale: The tmux/provider session layer still breaks several unrelated E2E narratives through prompt, restart, and child-session defects.
- Reason for existence: This plan exists to isolate the session-lifecycle and prompt-bootstrap problems into one parallel repair stream.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/checklists/16_e2e_real_runtime_gap_closure.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/contracts/parent_child/child_session_mergeback_contract.md`

## Scope

- Database: verify prompt, summary, attempt, and child-session merge-back records persist durably through real session use.
- CLI: use the real prompt, session, summary, and history commands as the proving surface.
- Daemon: repair tmux supervision, prompt delivery, child-session bootstrap, and liveness tracking.
- YAML: treat YAML as not the primary fix surface unless child-session prompt rendering depends on compiled metadata.
- Prompts: repair prompt ordering, unresolved placeholders, and idle-reminder surface expectations.
- Tests: rerun only the owned tmux/provider narratives until they either pass or expose a narrower downstream defect.
- Performance: keep the tmux/provider reruns isolated because these are the slowest and most resource-sensitive tests.
- Notes: log each session-lifecycle defect class separately so prompt issues do not get conflated with restart issues.

## Owned Files

- `tests/e2e/test_tmux_codex_idle_nudge_real.py`
- `tests/e2e/test_flow_07_pause_resume_and_recover_real.py`
- `tests/e2e/test_flow_13_human_gate_and_intervention_real.py`
- `tests/e2e/test_flow_21_child_session_round_trip_and_mergeback_real.py`
- `tests/e2e/test_e2e_prompt_and_summary_history_real.py`
- `tests/e2e/test_flow_05_admit_and_execute_node_run_real.py`

## Runtime Focus

- tmux session bootstrap
- prompt log / prompt delivery ordering
- live session liveness tracking
- supervision restart / replacement-session truth
- child-session prompt rendering and merge-back result recording
- idle reminder surfacing and prompt retrieval after admission

## Primary Failure Signatures

- `active node run not found` before `subtask prompt`
- session disappears before durable state is written
- prompt history ordering no longer matches assumptions
- unresolved `{{node_id}}` in child-session prompt
- `session show` reports the lost session instead of resumed replacement

## Plan

1. Fix prompt rendering and delivery for both primary and child sessions.
2. Fix the authoritative session-tracking model so supervision restart surfaces the replacement session.
3. Fix idle-nudge prompt retrieval so admitted task runs stay prompt-addressable.
4. Fix child-session merge-back result recording.
5. Rewrite any stale ordering assertions to match the real prompt history contract if the runtime behavior is correct.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/e2e/test_tmux_codex_idle_nudge_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_07_pause_resume_and_recover_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_13_human_gate_and_intervention_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_21_child_session_round_trip_and_mergeback_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_prompt_and_summary_history_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_05_admit_and_execute_node_run_real.py -q
```

## Exit Criteria

- owned tmux/provider E2Es reach their intended prompt/session state without session disappearance or broken prompt delivery
- child-session prompts render correctly and produce durable merge-back results
- restart and history surfaces reflect real runtime truth
