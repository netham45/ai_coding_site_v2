from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field


BackgroundHandler = Callable[[], None]


@dataclass(slots=True)
class BackgroundTaskRegistry:
    tasks: list[str] = field(default_factory=list)

    def register_placeholder(self, name: str) -> None:
        if name not in self.tasks:
            self.tasks.append(name)

    def snapshot(self) -> list[str]:
        return list(self.tasks)

