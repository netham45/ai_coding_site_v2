from __future__ import annotations

from tests.factories.sessions import heartbeat_fixture, session_event_fixture


def test_session_event_fixture_has_expected_shape() -> None:
    payload = session_event_fixture()

    assert payload["event_type"] == "heartbeat"
    assert payload["session_id"] == "session-scaffold"


def test_heartbeat_fixture_has_expected_shape() -> None:
    payload = heartbeat_fixture()

    assert payload["node_id"] == "node-scaffold"
    assert payload["heartbeat_at"].endswith("Z")

