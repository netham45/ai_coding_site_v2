from __future__ import annotations

from fastapi import HTTPException, status


class DaemonUnavailableError(HTTPException):
    def __init__(self, detail: str = "database unavailable") -> None:
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


class DaemonConflictError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class DaemonNotFoundError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
