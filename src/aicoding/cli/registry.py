from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


CommandHandler = Callable[[object], dict[str, object] | None]


@dataclass(frozen=True, slots=True)
class CommandSpec:
    path: tuple[str, ...]
    help_text: str
    handler: CommandHandler

