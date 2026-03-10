from __future__ import annotations


def session_event_fixture() -> dict[str, object]:
    return {
        "session_id": "session-scaffold",
        "event_type": "heartbeat",
        "recorded_at": "2026-03-08T00:00:00Z",
    }


def heartbeat_fixture() -> dict[str, object]:
    return {
        "session_id": "session-scaffold",
        "node_id": "node-scaffold",
        "heartbeat_at": "2026-03-08T00:00:00Z",
    }

