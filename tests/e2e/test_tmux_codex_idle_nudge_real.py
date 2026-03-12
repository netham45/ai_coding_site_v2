from __future__ import annotations

from pathlib import Path
import subprocess
import time

import pytest


def _tmux_capture(session_name: str) -> str:
    result = subprocess.run(
        ["tmux", "capture-pane", "-p", "-t", session_name],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return f"[tmux capture failed] {result.stderr.strip()}"
    return result.stdout


def _tmux_current_command(session_name: str) -> str:
    result = subprocess.run(
        ["tmux", "display-message", "-p", "-t", session_name, "#{pane_current_command}"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return f"[tmux command lookup failed] {result.stderr.strip()}"
    return result.stdout.strip()


def _tmux_pane_pid(session_name: str) -> str:
    result = subprocess.run(
        ["tmux", "display-message", "-p", "-t", session_name, "#{pane_pid}"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return f"[tmux pane pid lookup failed] {result.stderr.strip()}"
    return result.stdout.strip()


def _process_command_line(pid: str) -> str:
    result = subprocess.run(
        ["ps", "-p", pid, "-o", "args="],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return f"[ps command lookup failed] {result.stderr.strip()}"
    return result.stdout.strip()


def _cli_json(harness, *args: str) -> dict[str, object]:
    harness.assert_process_alive(prefix="Real daemon process exited before CLI inspection.")
    result = harness.cli(*args)
    assert result.exit_code == 0, result.stderr
    return result.json()


def _active_run_json_or_none(harness, *, node_id: str) -> dict[str, object] | None:
    result = harness.cli("node", "run", "show", "--node", node_id)
    if result.exit_code == 0:
        return result.json()
    if "active node run not found" in result.stderr:
        return None
    raise AssertionError(result.stderr)


def _session_show_json_or_none(harness, *, node_id: str) -> dict[str, object] | None:
    result = harness.cli("session", "show", "--node", node_id)
    if result.exit_code == 0:
        return result.json()
    if (
        "active node run not found" in result.stderr
        or "active durable run not found" in result.stderr
        or "session record not found" in result.stderr
    ):
        return None
    raise AssertionError(result.stderr)


def _create_manual_task_run(harness, *, task_prompt: str) -> str:
    epic_id = str(
        _cli_json(
            harness,
            "node",
            "create",
            "--kind",
            "epic",
            "--title",
            "Silent Until Nudged Epic",
            "--prompt",
            "Parent epic for tmux idle/nudge completion coverage.",
        )["node_id"]
    )
    phase_id = str(
        _cli_json(
            harness,
            "node",
            "child",
            "create",
            "--parent",
            epic_id,
            "--kind",
            "phase",
            "--title",
            "Silent Until Nudged Phase",
            "--prompt",
            "Parent phase for tmux idle/nudge completion coverage.",
        )["node_id"]
    )
    plan_id = str(
        _cli_json(
            harness,
            "node",
            "child",
            "create",
            "--parent",
            phase_id,
            "--kind",
            "plan",
            "--title",
            "Silent Until Nudged Plan",
            "--prompt",
            "Parent plan for tmux idle/nudge completion coverage.",
        )["node_id"]
    )
    task_id = str(
        _cli_json(
            harness,
            "node",
            "child",
            "create",
            "--parent",
            plan_id,
            "--kind",
            "task",
            "--title",
            "Silent Until Nudged Task",
            "--prompt",
            task_prompt,
        )["node_id"]
    )

    _cli_json(harness, "workflow", "compile", "--node", task_id)
    _cli_json(harness, "node", "lifecycle", "transition", "--node", task_id, "--state", "READY")
    _cli_json(harness, "node", "run", "start", "--node", task_id)
    return task_id


def _wait_for_daemon_nudge(
    harness,
    *,
    node_id: str,
    session_id: str,
    session_name: str,
    timeout_seconds: float = 90.0,
) -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object], str]:
    deadline = time.time() + timeout_seconds
    last_session_payload: dict[str, object] | None = None
    last_progress_payload: dict[str, object] | None = None
    last_summary_payload: dict[str, object] | None = None
    last_events_payload: dict[str, object] | None = None
    last_pane_text = ""
    active_session_id = session_id
    active_session_name = session_name

    while time.time() < deadline:
        harness.assert_process_alive(prefix="Real daemon process exited while waiting for a daemon idle nudge.")
        session_payload = _cli_json(harness, "session", "show", "--node", node_id)
        active_session_id = str(session_payload["session_id"])
        active_session_name = str(session_payload["session_name"])
        progress_payload = _cli_json(harness, "node", "run", "show", "--node", node_id)
        summary_payload = _cli_json(harness, "summary", "history", "--node", node_id)
        events_payload = _cli_json(harness, "session", "events", "--session", active_session_id)
        last_pane_text = _tmux_capture(active_session_name)
        last_session_payload = session_payload
        last_progress_payload = progress_payload
        last_summary_payload = summary_payload
        last_events_payload = events_payload

        latest_attempt = progress_payload["latest_attempt"]
        assert summary_payload["summaries"] == [], (
            "The task session registered summary history before a daemon-originated nudge.\n"
            f"session_name={session_name}\n"
            f"pane_text=\n{last_pane_text}\n"
            f"events_payload={events_payload}"
        )
        assert progress_payload["state"]["last_completed_compiled_subtask_id"] is None, (
            "The task session completed the subtask before a daemon-originated nudge.\n"
            f"session_name={session_name}\n"
            f"pane_text=\n{last_pane_text}\n"
            f"events_payload={events_payload}"
        )
        if latest_attempt is not None:
            assert latest_attempt["status"] != "COMPLETE", (
                "The task session marked the attempt complete before a daemon-originated nudge.\n"
                f"session_name={session_name}\n"
                f"pane_text=\n{last_pane_text}\n"
                f"events_payload={events_payload}"
            )
        if any(event["event_type"] == "nudged" for event in events_payload["events"]):
            break
        time.sleep(2.0)

    assert last_session_payload is not None
    assert last_progress_payload is not None
    assert last_summary_payload is not None
    assert last_events_payload is not None
    return last_session_payload, last_progress_payload, last_summary_payload, last_events_payload, last_pane_text


def _assert_confirmed_idle_state_immediately_before_nudge(*, events_payload: dict[str, object], session_name: str, pane_text: str) -> None:
    nudged_index = next(index for index, event in enumerate(events_payload["events"]) if event["event_type"] == "nudged")
    prior_screen_events = [
        event for event in events_payload["events"][:nudged_index] if event["event_type"] == "screen_polled"
    ]
    assert prior_screen_events, (
        "The daemon nudged without any prior screen polling evidence.\n"
        f"session_name={session_name}\n"
        f"pane_text=\n{pane_text}\n"
        f"events_payload={events_payload}"
    )
    last_screen_event = prior_screen_events[-1]
    payload = last_screen_event["payload_json"]
    assert payload.get("classification") == "idle", (
        "The last screen state before nudge was not idle.\n"
        f"session_name={session_name}\n"
        f"last_screen_event={last_screen_event}\n"
        f"pane_text=\n{pane_text}\n"
        f"events_payload={events_payload}"
    )
    assert payload.get("reason") == "unchanged_screen_past_idle_threshold", (
        "The daemon nudged without a confirmed unchanged-screen idle state immediately beforehand.\n"
        f"session_name={session_name}\n"
        f"last_screen_event={last_screen_event}\n"
        f"pane_text=\n{pane_text}\n"
        f"events_payload={events_payload}"
    )
    assert "active_work_marker" not in payload, (
        "The final pre-nudge screen evidence still carried an active-work marker.\n"
        f"session_name={session_name}\n"
        f"last_screen_event={last_screen_event}\n"
        f"pane_text=\n{pane_text}\n"
        f"events_payload={events_payload}"
    )


def _assert_no_meaningful_pre_nudge_chatter(*, pane_text: str, session_name: str) -> None:
    forbidden_snippets = (
        "I’m pulling the subtask prompt",
        "I’m fetching the subtask prompt",
        "I’m reading the subtask prompt",
        "I have the subtask instructions.",
        "I’ve resolved the live compiled subtask id",
        "I haven’t seen the actual idle reminder yet.",
        "I’m checking the local code and tests",
        "I’m tracing the installed aicoding package",
        "then I’ll execute whatever work it specifies",
        "then I’ll carry out whatever work it specifies",
        "then I’ll execute whatever work it describes",
        "then I’ll carry out whatever work it describes",
    )
    found = [snippet for snippet in forbidden_snippets if snippet in pane_text]
    assert not found, (
        "The tmux session produced meaningful pre-nudge chatter instead of actually waiting idle.\n"
        f"session_name={session_name}\n"
        f"found_snippets={found}\n"
        f"pane_text=\n{pane_text}"
    )


def _assert_no_pseudo_idle_shell_activity(*, pane_text: str, session_name: str) -> None:
    forbidden_snippets = (
        "\n/ps\n",
        "Background terminals",
        "sleep 70",
        "sleep 60",
        "sleep 30",
    )
    found = [snippet for snippet in forbidden_snippets if snippet in pane_text]
    assert not found, (
        "The tmux session used shell or background-terminal activity instead of remaining genuinely idle before the daemon nudge.\n"
        f"session_name={session_name}\n"
        f"found_snippets={found}\n"
        f"pane_text=\n{pane_text}"
    )


def _wait_for_post_nudge_completion(
    harness,
    *,
    node_id: str,
    session_id: str,
    session_name: str,
    timeout_seconds: float = 90.0,
) -> tuple[dict[str, object] | None, dict[str, object], dict[str, object] | None, dict[str, object], dict[str, object], str]:
    deadline = time.time() + timeout_seconds
    last_progress_payload: dict[str, object] | None = None
    last_runs_payload: dict[str, object] | None = None
    last_summary_payload: dict[str, object] | None = None
    last_session_payload: dict[str, object] | None = None
    last_events_payload: dict[str, object] | None = None
    last_pane_text = ""
    active_session_id = session_id
    active_session_name = session_name

    while time.time() < deadline:
        harness.assert_process_alive(prefix="Real daemon process exited while waiting for post-nudge completion.")
        progress_payload = _active_run_json_or_none(harness, node_id=node_id)
        runs_payload = _cli_json(harness, "node", "runs", "--node", node_id)
        summary_payload = _cli_json(harness, "summary", "history", "--node", node_id)
        session_payload = _session_show_json_or_none(harness, node_id=node_id)
        if session_payload is not None:
            active_session_id = str(session_payload["session_id"])
            active_session_name = str(session_payload["session_name"])
        events_payload = _cli_json(harness, "session", "events", "--session", active_session_id)
        last_pane_text = _tmux_capture(active_session_name)
        last_progress_payload = progress_payload
        last_runs_payload = runs_payload
        last_summary_payload = summary_payload
        last_session_payload = session_payload
        last_events_payload = events_payload

        latest_attempt = None if progress_payload is None else progress_payload["latest_attempt"]
        latest_run = runs_payload["runs"][0]
        if latest_attempt is not None and latest_attempt["status"] == "COMPLETE" and summary_payload["summaries"]:
            break
        if latest_run["run_status"] == "COMPLETE" and summary_payload["summaries"]:
            break
        time.sleep(2.0)

    assert last_runs_payload is not None
    assert last_summary_payload is not None
    assert last_events_payload is not None
    return last_progress_payload, last_runs_payload, last_summary_payload, last_session_payload, last_events_payload, last_pane_text


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_tmux_primary_session_launches_codex_not_shell(real_daemon_harness_factory) -> None:
    harness = real_daemon_harness_factory(
        session_backend="tmux",
        extra_env={
            "AICODING_SESSION_IDLE_THRESHOLD_SECONDS": "5.0",
            "AICODING_SESSION_POLL_INTERVAL_SECONDS": "0.2",
        },
    )
    sessions_to_cleanup: set[str] = set()
    try:
        start_result = harness.cli(
            "workflow",
            "start",
            "--kind",
            "epic",
            "--title",
            "Real Tmux Codex Launch Node",
            "--prompt",
            "Launch a real Codex session in tmux and begin the current prompt.",
        )
        assert start_result.exit_code == 0, start_result.stderr
        node_id = str(start_result.json()["node"]["node_id"])

        bind_result = harness.cli("session", "bind", "--node", node_id)
        assert bind_result.exit_code == 0, bind_result.stderr
        bind_payload = bind_result.json()
        session_name = str(bind_payload["session_name"])
        sessions_to_cleanup.add(session_name)

        pane_command = ""
        pane_pid = ""
        process_command_line = ""
        pane_text = ""
        deadline = time.time() + 20.0
        while time.time() < deadline:
            pane_command = _tmux_current_command(session_name)
            pane_pid = _tmux_pane_pid(session_name)
            if pane_pid and not pane_pid.startswith("[tmux pane pid lookup failed]"):
                process_command_line = _process_command_line(pane_pid)
            pane_text = _tmux_capture(session_name)
            if "codex" in process_command_line:
                break
            time.sleep(1.0)

        assert bind_payload["tmux_session_exists"] is True
        assert bind_payload["logical_node_id"] == node_id
        assert "codex" in process_command_line, (
            "Expected the live primary tmux session to reach a Codex process after bootstrap.\n"
            f"session_name={session_name}\n"
            f"pane_current_command={pane_command}\n"
            f"pane_pid={pane_pid}\n"
            f"process_command_line={process_command_line}\n"
            f"pane_text=\n{pane_text}"
        )
    finally:
        for session_name in sessions_to_cleanup:
            subprocess.run(["tmux", "kill-session", "-t", session_name], check=False, capture_output=True, text=True)


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_tmux_primary_session_exports_prompt_log_for_live_codex_bootstrap(real_daemon_harness_factory) -> None:
    harness = real_daemon_harness_factory(
        session_backend="tmux",
        extra_env={
            "AICODING_SESSION_IDLE_THRESHOLD_SECONDS": "10.0",
            "AICODING_SESSION_POLL_INTERVAL_SECONDS": "0.2",
        },
    )
    sessions_to_cleanup: set[str] = set()
    try:
        start_result = harness.cli(
            "workflow",
            "start",
            "--kind",
            "epic",
            "--title",
            "Real Tmux Codex Prompt Bootstrap Node",
            "--prompt",
            "Launch a real Codex session in tmux and bootstrap it with the current-stage prompt.",
        )
        assert start_result.exit_code == 0, start_result.stderr
        node_id = str(start_result.json()["node"]["node_id"])

        prompt_result = harness.cli("subtask", "prompt", "--node", node_id)
        bind_result = harness.cli("session", "bind", "--node", node_id)
        events_result = harness.cli("session", "events", "--session", str(bind_result.json()["session_id"]))

        assert prompt_result.exit_code == 0, prompt_result.stderr
        assert bind_result.exit_code == 0, bind_result.stderr
        assert events_result.exit_code == 0, events_result.stderr

        prompt_payload = prompt_result.json()
        bind_payload = bind_result.json()
        event_payload = events_result.json()["events"][0]["payload_json"]
        prompt_log_path = str(event_payload["prompt_log_path"])
        session_name = str(bind_payload["session_name"])
        sessions_to_cleanup.add(session_name)

        deadline = time.time() + 20.0
        while time.time() < deadline:
            if Path(prompt_log_path).is_file():
                break
            time.sleep(2.0)

        assert bind_payload["tmux_session_exists"] is True
        assert event_payload["prompt_cli_command"]
        assert "prompt_logs" in prompt_log_path
        assert prompt_payload["prompt_text"]
        prompt_log_file = Path(prompt_log_path)
        assert prompt_log_file.is_file(), (
            "Expected the Codex bootstrap helper to write the prompt log file recorded in the session event.\n"
            f"prompt_log_path={prompt_log_path}\n"
        )
        assert prompt_payload["prompt_text"].strip() in prompt_log_file.read_text(encoding="utf-8")
    finally:
        for session_name in sessions_to_cleanup:
            subprocess.run(["tmux", "kill-session", "-t", session_name], check=False, capture_output=True, text=True)


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_tmux_task_session_stays_quiet_until_daemon_nudges_then_reports_completion(real_daemon_harness_factory) -> None:
    harness = real_daemon_harness_factory(
        session_backend="tmux",
        extra_env={
            "AICODING_SESSION_IDLE_THRESHOLD_SECONDS": "5.0",
            "AICODING_SESSION_POLL_INTERVAL_SECONDS": "0.2",
            "AICODING_SESSION_MAX_NUDGE_COUNT": "2",
        },
    )
    sessions_to_cleanup: set[str] = set()
    try:
        task_prompt = (
            "For this test, your only job before the real idle nudge arrives is to wait silently. Do not start the subtask attempt, "
            "do not load extra context, do not inspect tests, do not inspect the local package, do not create files, do not register "
            "a summary, do not complete the subtask, do not use slash commands, do not open background terminals, do not run sleep or "
            "other shell waiting commands, and do not emit progress chatter before the idle nudge reminder appears in tmux. "
            "Before the nudge, you may emit at most one short plain-language status line saying that you are waiting and have not "
            "started subtask work; do not register that status line as a summary. "
            "After you receive that nudge, create summaries/implementation.md "
            "containing exactly 'nudged completion body', then run `python3 -m aicoding.cli.main summary register --node "
            "THE_NODE_ID_FROM_THIS_PROMPT --file summaries/implementation.md --type subtask`, then run "
            "`python3 -m aicoding.cli.main subtask current --node THE_NODE_ID_FROM_THIS_PROMPT` to get the live compiled subtask id, and "
            "then run `python3 -m aicoding.cli.main subtask complete --node THE_NODE_ID_FROM_THIS_PROMPT --compiled-subtask CURRENT_ID "
            "--summary \"nudged completion\"`. Stay silent while waiting for the nudge."
        )
        node_id = _create_manual_task_run(harness, task_prompt=task_prompt)

        prompt_payload = _cli_json(harness, "subtask", "prompt", "--node", node_id)
        bind_payload = _cli_json(harness, "session", "bind", "--node", node_id)
        session_id = str(bind_payload["session_id"])
        session_name = str(bind_payload["session_name"])
        sessions_to_cleanup.add(session_name)

        assert "do not register a summary" in str(prompt_payload["prompt_text"])
        assert "nudged completion body" in str(prompt_payload["prompt_text"])
        assert bind_payload["logical_node_id"] == node_id
        assert bind_payload["tmux_session_exists"] is True

        nudged_session_payload, pre_nudge_progress, pre_nudge_summary_history, pre_nudge_events, pre_nudge_pane = _wait_for_daemon_nudge(
            harness,
            node_id=node_id,
            session_id=session_id,
            session_name=session_name,
        )
        effective_session_id = str(nudged_session_payload["session_id"])
        effective_session_name = str(nudged_session_payload["session_name"])
        sessions_to_cleanup.add(effective_session_name)

        assert any(event["event_type"] == "nudged" for event in pre_nudge_events["events"]), (
            "Expected the daemon to record a nudged event after a real idle timeout.\n"
            f"session_name={session_name}\n"
            f"pane_text=\n{pre_nudge_pane}\n"
            f"events_payload={pre_nudge_events}"
        )
        idle_screen_events = [
            event for event in pre_nudge_events["events"] if event["event_type"] == "screen_polled"
        ]
        assert any(
            event["payload_json"].get("classification") == "idle"
            and event["payload_json"].get("reason") == "unchanged_screen_past_idle_threshold"
            for event in idle_screen_events
        ), (
            "Expected the daemon to observe confirmed unchanged-screen idle before nudging.\n"
            f"session_name={session_name}\n"
            f"pane_text=\n{pre_nudge_pane}\n"
            f"events_payload={pre_nudge_events}"
        )
        first_nudged_index = next(
            index for index, event in enumerate(pre_nudge_events["events"]) if event["event_type"] == "nudged"
        )
        assert any(
            event["event_type"] == "screen_polled"
            and event["payload_json"].get("classification") == "idle"
            and event["payload_json"].get("reason") == "unchanged_screen_past_idle_threshold"
            for event in pre_nudge_events["events"][:first_nudged_index]
        ), (
            "The daemon nudged before recording confirmed unchanged-screen idle.\n"
            f"session_name={session_name}\n"
            f"pane_text=\n{pre_nudge_pane}\n"
            f"events_payload={pre_nudge_events}"
        )
        _assert_confirmed_idle_state_immediately_before_nudge(
            events_payload=pre_nudge_events,
            session_name=session_name,
            pane_text=pre_nudge_pane,
        )
        _assert_no_meaningful_pre_nudge_chatter(
            pane_text=pre_nudge_pane,
            session_name=session_name,
        )
        _assert_no_pseudo_idle_shell_activity(
            pane_text=pre_nudge_pane,
            session_name=session_name,
        )
        assert "Your session appears idle on node" in pre_nudge_pane
        assert "{{node_id}}" not in pre_nudge_pane

        post_nudge_progress, post_nudge_runs, post_nudge_summary_history, post_nudge_session, post_nudge_events, post_nudge_pane = (
            _wait_for_post_nudge_completion(
                harness,
                node_id=node_id,
                session_id=effective_session_id,
                session_name=effective_session_name,
            )
        )

        latest_attempt_after = None if post_nudge_progress is None else post_nudge_progress["latest_attempt"]
        latest_run_after = post_nudge_runs["runs"][0]
        assert (
            latest_attempt_after is not None or latest_run_after["run_status"] == "COMPLETE"
        ), (
            "Expected either a durable completed attempt or a durably completed latest run after nudging the idle task session.\n"
            f"session_name={session_name}\n"
            f"pane_before_nudge=\n{pre_nudge_pane}\n"
            f"pane_after_nudge=\n{post_nudge_pane}\n"
            f"runs_payload={post_nudge_runs}"
        )
        if latest_attempt_after is not None:
            assert latest_attempt_after["status"] == "COMPLETE", (
                "Expected the task session to complete only after the nudge.\n"
                f"session_name={session_name}\n"
                f"pane_before_nudge=\n{pre_nudge_pane}\n"
                f"pane_after_nudge=\n{post_nudge_pane}"
            )
            assert latest_attempt_after["summary"] == "nudged completion"
        else:
            assert latest_run_after["run_status"] == "COMPLETE", (
                "The active run disappeared after the nudge, but the latest durable run is not complete.\n"
                f"session_name={session_name}\n"
                f"pane_before_nudge=\n{pre_nudge_pane}\n"
                f"pane_after_nudge=\n{post_nudge_pane}\n"
                f"runs_payload={post_nudge_runs}"
            )
        assert post_nudge_summary_history["summaries"], (
            "Expected a durable registered summary after the nudge.\n"
            f"session_name={session_name}\n"
            f"pane_before_nudge=\n{pre_nudge_pane}\n"
            f"pane_after_nudge=\n{post_nudge_pane}"
        )
        assert pre_nudge_pane != post_nudge_pane
        nudged_events = [event for event in post_nudge_events["events"] if event["event_type"] == "nudged"]
        assert nudged_events, (
            "Expected at least one daemon-originated nudge event in the durable session history.\n"
            f"session_name={session_name}\n"
            f"events_payload={post_nudge_events}"
        )
        assert len(nudged_events) == 1, (
            "The daemon emitted repeated nudges for the same task-session flow even after post-nudge completion progress began.\n"
            f"session_name={session_name}\n"
            f"pane_before_nudge=\n{pre_nudge_pane}\n"
            f"pane_after_nudge=\n{post_nudge_pane}\n"
            f"events_payload={post_nudge_events}"
        )

        summary_id = str(post_nudge_summary_history["summaries"][0]["id"])
        summary_show = _cli_json(harness, "summary", "show", "--summary", summary_id)
        assert str(summary_show["content"]).strip() == "nudged completion body"
        if post_nudge_session is not None:
            assert post_nudge_session["session_id"] == effective_session_id
    finally:
        for session_name in sessions_to_cleanup:
            subprocess.run(["tmux", "kill-session", "-t", session_name], check=False, capture_output=True, text=True)
