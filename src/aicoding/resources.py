from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aicoding.bootstrap import PACKAGE_ROOT
from aicoding.config import Settings, get_settings
from aicoding.errors import ConfigurationError
from aicoding.resource_models import (
    LoadedResourceText,
    PromptAssetMetadata,
    ResourceFileDescriptor,
    YamlAssetMetadata,
)


@dataclass(frozen=True, slots=True)
class ResourceCatalog:
    root: Path
    yaml_builtin_dir: Path
    yaml_builtin_system_dir: Path
    yaml_project_dir: Path
    yaml_project_policies_dir: Path
    yaml_overrides_dir: Path
    yaml_schemas_dir: Path
    prompt_layouts_dir: Path
    prompt_execution_dir: Path
    prompt_recovery_dir: Path
    prompt_quality_dir: Path
    prompt_pack_default_dir: Path
    prompt_project_dir: Path
    docs_dir: Path

    def group_paths(self) -> dict[str, Path]:
        return {
            "yaml_builtin": self.yaml_builtin_dir,
            "yaml_builtin_system": self.yaml_builtin_system_dir,
            "yaml_project": self.yaml_project_dir,
            "yaml_project_policies": self.yaml_project_policies_dir,
            "yaml_overrides": self.yaml_overrides_dir,
            "yaml_schemas": self.yaml_schemas_dir,
            "prompt_layouts": self.prompt_layouts_dir,
            "prompt_execution": self.prompt_execution_dir,
            "prompt_recovery": self.prompt_recovery_dir,
            "prompt_quality": self.prompt_quality_dir,
            "prompt_pack_default": self.prompt_pack_default_dir,
            "prompt_project": self.prompt_project_dir,
            "docs": self.docs_dir,
        }

    def resolve(self, group: str, relative_path: str) -> Path:
        try:
            base = self.group_paths()[group]
        except KeyError as exc:
            raise ConfigurationError(
                message=f"Unknown resource group: {group}",
                code="resource_group_unknown",
                details={"group": group},
            ) from exc

        relative = Path(relative_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ConfigurationError(
                message="Resource path escapes its configured group root.",
                code="resource_path_escape",
                details={"group": group, "relative_path": relative_path},
            )
        return base / relative

    def read_text(self, group: str, relative_path: str) -> str:
        path = self.resolve(group, relative_path)
        return path.read_text(encoding="utf-8")

    def describe(self, group: str, relative_path: str) -> ResourceFileDescriptor:
        path = self.resolve(group, relative_path)
        return ResourceFileDescriptor(group=group, relative_path=relative_path, absolute_path=path)

    def load_text(self, group: str, relative_path: str) -> LoadedResourceText:
        descriptor = self.describe(group, relative_path)
        return LoadedResourceText(descriptor=descriptor, content=descriptor.absolute_path.read_text(encoding="utf-8"))

    def yaml_metadata(self, group: str, relative_path: str) -> YamlAssetMetadata:
        descriptor = self.describe(group, relative_path)
        family = Path(relative_path).parts[0] if Path(relative_path).parts else ""
        return YamlAssetMetadata(
            source_group=descriptor.group,
            family=family,
            relative_path=descriptor.relative_path,
            extension=descriptor.absolute_path.suffix,
        )

    def prompt_metadata(self, group: str, relative_path: str) -> PromptAssetMetadata:
        descriptor = self.describe(group, relative_path)
        relative = Path(relative_path)
        parts = relative.parts
        scope = parts[0] if parts else ""
        pack = parts[0] if group == "prompt_pack_default" and parts else None
        if group == "prompt_pack_default" and len(parts) >= 2:
            scope = parts[0]
            pack = "default"
        return PromptAssetMetadata(
            source_group=descriptor.group,
            scope=scope,
            pack=pack,
            relative_path=descriptor.relative_path,
            extension=descriptor.absolute_path.suffix,
        )


def load_resource_catalog(settings: Settings | None = None) -> ResourceCatalog:
    resolved_settings = settings or get_settings()
    package_root = PACKAGE_ROOT / "resources"
    workspace_root = resolved_settings.workspace_root
    workspace_resources_root = (workspace_root / "resources") if workspace_root is not None else package_root
    return ResourceCatalog(
        root=package_root,
        yaml_builtin_dir=package_root / "yaml" / "builtin",
        yaml_builtin_system_dir=package_root / "yaml" / "builtin" / "system-yaml",
        yaml_project_dir=workspace_resources_root / "yaml" / "project",
        yaml_project_policies_dir=workspace_resources_root / "yaml" / "project" / "project-policies",
        yaml_overrides_dir=workspace_resources_root / "yaml" / "overrides",
        yaml_schemas_dir=package_root / "yaml" / "schemas",
        prompt_layouts_dir=package_root / "prompts" / "layouts",
        prompt_execution_dir=package_root / "prompts" / "execution",
        prompt_recovery_dir=package_root / "prompts" / "recovery",
        prompt_quality_dir=package_root / "prompts" / "quality",
        prompt_pack_default_dir=package_root / "prompts" / "packs" / "default",
        prompt_project_dir=workspace_resources_root / "prompts" / "project",
        docs_dir=workspace_resources_root / "docs",
    )
