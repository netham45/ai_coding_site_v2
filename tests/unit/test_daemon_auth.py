from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from aicoding.config import Settings
from aicoding.daemon.auth import initialize_auth_context, require_bearer_token


def _build_auth_test_client(tmp_path: Path, *, token: str = "secret") -> TestClient:
    app = FastAPI()
    settings = Settings(auth_token=token, auth_token_file=tmp_path / ".runtime" / "daemon.token")
    app.state.settings = settings
    app.state.auth_context = initialize_auth_context(settings)

    @app.get("/protected", dependencies=[Depends(require_bearer_token)])
    def protected() -> dict[str, str]:
        return {"status": "ok"}

    return TestClient(app)


def test_require_bearer_token_rejects_missing_header(tmp_path: Path) -> None:
    with _build_auth_test_client(tmp_path) as client:
        response = client.get("/protected")

    assert response.status_code == 401
    assert response.json()["detail"] == "missing bearer token"


def test_require_bearer_token_rejects_invalid_token(tmp_path: Path) -> None:
    with _build_auth_test_client(tmp_path) as client:
        response = client.get("/protected", headers={"Authorization": "Bearer wrong"})

    assert response.status_code == 401
    assert response.json()["detail"] == "invalid bearer token"


def test_require_bearer_token_accepts_valid_token(tmp_path: Path) -> None:
    with _build_auth_test_client(tmp_path, token="valid-token") as client:
        response = client.get("/protected", headers={"Authorization": "Bearer valid-token"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
