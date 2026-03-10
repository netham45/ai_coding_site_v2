from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import Field, ValidationError, model_validator

from aicoding.models.base import AICodingModel


class FlowAssetValidationError(ValueError):
    """Raised when a flow YAML asset cannot be parsed or validated."""


class FlowYamlAsset(AICodingModel):
    id: str
    name: str
    purpose: str
    simulation_sources: list[str] = Field(min_length=1)
    covers: list[str] = Field(min_length=1)
    entry_conditions: list[str] = Field(min_length=1)
    task_flow: list[str] = Field(min_length=1)
    required_subtasks: list[str] = Field(min_length=1)
    required_capabilities: list[str] = Field(min_length=1)
    expected_tests: list[str] = Field(min_length=1)
    known_limitations: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def normalize_and_validate(self) -> "FlowYamlAsset":
        self.id = self.id.strip()
        self.name = self.name.strip()
        self.purpose = self.purpose.strip()
        if not self.id:
            raise ValueError("flow asset id may not be blank")
        if not self.name:
            raise ValueError("flow asset name may not be blank")
        if not self.purpose:
            raise ValueError("flow asset purpose may not be blank")
        return self


def discover_flow_yaml_paths(flows_dir: Path) -> list[Path]:
    return sorted(path for path in flows_dir.glob("*.yaml") if path.is_file())


def load_flow_yaml_asset(path: Path) -> FlowYamlAsset:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise FlowAssetValidationError(f"invalid YAML in {path.name}: {exc}") from exc

    if not isinstance(raw, dict):
        raise FlowAssetValidationError(f"{path.name} must contain a top-level mapping")

    try:
        asset = FlowYamlAsset.model_validate(raw)
    except ValidationError as exc:
        raise FlowAssetValidationError(f"invalid flow asset {path.name}: {exc}") from exc

    expected_id = path.stem
    if asset.id != expected_id:
        raise FlowAssetValidationError(
            f"flow asset id '{asset.id}' does not match filename stem '{expected_id}'"
        )

    return asset


def load_flow_yaml_assets(flows_dir: Path) -> list[FlowYamlAsset]:
    return [load_flow_yaml_asset(path) for path in discover_flow_yaml_paths(flows_dir)]
