from __future__ import annotations

from dataclasses import dataclass

import httpx

from aicoding.auth import load_auth_token
from aicoding.config import Settings, get_settings
from aicoding.errors import CommandExecutionError


def _raise_for_error_response(
    *,
    base_url: str,
    path: str,
    status_code: int,
    payload: dict[str, object],
) -> None:
    details = {
        "base_url": base_url,
        "path": path,
        "status_code": status_code,
        "response": payload,
    }
    if status_code == 404:
        raise CommandExecutionError(
            message="The requested daemon resource was not found.",
            code="not_found",
            exit_code=4,
            details=details,
        )
    if status_code == 409:
        raise CommandExecutionError(
            message="The daemon rejected the request because of a state conflict.",
            code="daemon_conflict",
            exit_code=4,
            details=details,
        )
    raise CommandExecutionError(
        message="The daemon returned an error response.",
        code="daemon_request_failed",
        details=details,
    )


@dataclass(frozen=True, slots=True)
class DaemonClient:
    base_url: str
    token: str
    timeout_seconds: float = 5.0

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    def request(self, method: str, path: str, *, json_payload: dict[str, object] | None = None) -> dict[str, object]:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.request(method, url, json=json_payload, headers=self._headers())
        except httpx.HTTPError as exc:
            raise CommandExecutionError(
                message="The daemon is unavailable.",
                code="daemon_unavailable",
                details={"base_url": self.base_url, "reason": str(exc)},
            ) from exc

        try:
            payload = response.json()
        except ValueError:
            payload = {"status_code": response.status_code, "body": response.text}

        if response.is_error:
            _raise_for_error_response(
                base_url=self.base_url,
                path=path,
                status_code=response.status_code,
                payload=payload,
            )
        return payload


def build_daemon_base_url(settings: Settings | None = None) -> str:
    active_settings = settings or get_settings()
    return active_settings.daemon.base_url


def build_daemon_client(settings: Settings | None = None) -> DaemonClient:
    active_settings = settings or get_settings()
    return DaemonClient(
        base_url=build_daemon_base_url(active_settings),
        token=load_auth_token(settings=active_settings),
        timeout_seconds=active_settings.daemon.request_timeout_seconds,
    )
