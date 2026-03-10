from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aicoding.resources import ResourceCatalog, load_resource_catalog


@dataclass(frozen=True, slots=True)
class LoadedResource:
    group: str
    path: Path
    content: str


def catalog() -> ResourceCatalog:
    return load_resource_catalog()


def load_text(group: str, relative_path: str) -> LoadedResource:
    resource_catalog = catalog()
    path = resource_catalog.resolve(group, relative_path)
    return LoadedResource(group=group, path=path, content=path.read_text(encoding="utf-8"))


def list_relative_files(root: Path) -> list[str]:
    return sorted(str(path.relative_to(root)) for path in root.rglob("*") if path.is_file())

