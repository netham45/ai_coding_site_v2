from __future__ import annotations

from aicoding.errors import ApplicationError


def test_application_error_payload_includes_details() -> None:
    error = ApplicationError(message="boom", code="test_error", details={"field": "value"})

    assert error.to_payload() == {
        "error": "test_error",
        "message": "boom",
        "details": {"field": "value"},
    }

