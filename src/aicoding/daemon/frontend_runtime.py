from __future__ import annotations

import json
from pathlib import Path

from fastapi import Request
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, Response

from aicoding.config import Settings
from aicoding.daemon.auth import get_runtime_bearer_token

FRONTEND_BOOTSTRAP_GLOBAL = "__AICODING_DAEMON_BOOTSTRAP__"


def resolve_frontend_dist_dir() -> Path | None:
    repo_candidate = Path(__file__).resolve().parents[3] / "frontend" / "dist"
    cwd_candidate = Path.cwd() / "frontend" / "dist"

    for candidate in (repo_candidate, cwd_candidate):
        if (candidate / "index.html").exists():
            return candidate
    return None


def serve_frontend_asset(asset_path: str) -> Response:
    dist_dir = resolve_frontend_dist_dir()
    if dist_dir is None:
        return PlainTextResponse(
            "Compiled frontend assets are unavailable. Run `cd frontend && npm run build` first.",
            status_code=503,
        )

    target = (dist_dir / "assets" / asset_path).resolve()
    assets_root = (dist_dir / "assets").resolve()
    if assets_root not in target.parents or not target.is_file():
        return PlainTextResponse("Frontend asset not found.", status_code=404)
    return FileResponse(target)


def serve_frontend_index(request: Request, *, settings: Settings) -> Response:
    dist_dir = resolve_frontend_dist_dir()
    if dist_dir is None:
        return PlainTextResponse(
            "Compiled frontend assets are unavailable. Run `cd frontend && npm run build` first.",
            status_code=503,
        )

    index_html = (dist_dir / "index.html").read_text(encoding="utf-8")
    payload = {
        "apiBaseUrl": "/api",
        "apiToken": get_runtime_bearer_token(request),
        "daemonBaseUrl": settings.daemon.base_url,
        "daemonAppName": settings.daemon_app_name,
    }
    script_payload = json.dumps(payload, separators=(",", ":")).replace("<", "\\u003c")
    injection = (
        f'<script>window.{FRONTEND_BOOTSTRAP_GLOBAL}={script_payload};</script>'
    )
    rendered_html = index_html.replace("</head>", f"  {injection}\n  </head>", 1)
    return HTMLResponse(rendered_html)
