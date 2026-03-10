from __future__ import annotations

from dataclasses import dataclass

from aicoding.config import Settings, get_settings
from aicoding.resources import ResourceCatalog, load_resource_catalog


@dataclass(frozen=True, slots=True)
class CliContext:
    settings: Settings
    resources: ResourceCatalog


def build_cli_context() -> CliContext:
    return CliContext(
        settings=get_settings(),
        resources=load_resource_catalog(),
    )

