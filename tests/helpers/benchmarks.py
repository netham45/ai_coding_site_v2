from __future__ import annotations

import os
from time import perf_counter
from typing import Callable, TypeVar


T = TypeVar("T")


def measure(func: Callable[[], T]) -> tuple[T, float]:
    start = perf_counter()
    result = func()
    elapsed = perf_counter() - start
    return result, elapsed


def xdist_contention_budget(base_budget: float, *, xdist_budget: float) -> float:
    if os.environ.get("PYTEST_XDIST_WORKER"):
        return xdist_budget
    return base_budget
