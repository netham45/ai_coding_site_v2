from __future__ import annotations

from time import perf_counter
from typing import Callable, TypeVar


T = TypeVar("T")


def measure(func: Callable[[], T]) -> tuple[T, float]:
    start = perf_counter()
    result = func()
    elapsed = perf_counter() - start
    return result, elapsed

