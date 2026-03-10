from __future__ import annotations

from pathlib import Path
from typing import Literal

from aicoding.models.base import AICodingModel

ResourceGroup = Literal[
    "yaml_builtin",
    "yaml_builtin_system",
    "yaml_project",
    "yaml_project_policies",
    "yaml_overrides",
    "yaml_schemas",
    "prompt_layouts",
    "prompt_execution",
    "prompt_recovery",
    "prompt_quality",
    "prompt_pack_default",
    "prompt_project",
    "docs",
]


class ResourceFileDescriptor(AICodingModel):
    group: ResourceGroup
    relative_path: str
    absolute_path: Path


class LoadedResourceText(AICodingModel):
    descriptor: ResourceFileDescriptor
    content: str


class YamlAssetMetadata(AICodingModel):
    source_group: ResourceGroup
    family: str
    relative_path: str
    extension: str


class PromptAssetMetadata(AICodingModel):
    source_group: ResourceGroup
    scope: str
    pack: str | None = None
    relative_path: str
    extension: str
