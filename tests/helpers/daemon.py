from __future__ import annotations

from dataclasses import dataclass

from fastapi.testclient import TestClient

from aicoding.cli.daemon_client import _raise_for_error_response


@dataclass(frozen=True, slots=True)
class DaemonBridgeClient:
    client: TestClient
    token: str

    def request(self, method: str, path: str, json_payload: dict[str, object] | None = None) -> dict[str, object]:
        headers = {"Authorization": f"Bearer {self.token}"}
        if method == "GET":
            response = self.client.get(path, headers=headers)
        else:
            response = self.client.post(path, headers=headers, json=json_payload)
        payload = response.json()
        if response.is_error:
            _raise_for_error_response(
                base_url=str(self.client.base_url),
                path=path,
                status_code=response.status_code,
                payload=payload,
            )
        return payload
