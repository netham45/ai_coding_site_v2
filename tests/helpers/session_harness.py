from __future__ import annotations

from datetime import datetime, timedelta, timezone


class FakeClock:
    def __init__(self) -> None:
        self.current = datetime(2026, 3, 8, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self.current

    def advance(self, *, seconds: float) -> None:
        self.current += timedelta(seconds=seconds)

