from __future__ import annotations

import uvicorn

from aicoding.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "aicoding.daemon.app:create_app",
        factory=True,
        host=settings.daemon_host,
        port=settings.daemon_port,
    )


if __name__ == "__main__":
    main()

