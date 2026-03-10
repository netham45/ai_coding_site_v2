from __future__ import annotations

from pathlib import Path

import pytest

from aicoding.flow_assets import (
    FlowAssetValidationError,
    discover_flow_yaml_paths,
    load_flow_yaml_asset,
    load_flow_yaml_assets,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_load_flow_yaml_asset_accepts_valid_asset(tmp_path: Path) -> None:
    path = tmp_path / "14_project_bootstrap_and_yaml_onboarding_flow.yaml"
    path.write_text(
        "\n".join(
            [
                "id: 14_project_bootstrap_and_yaml_onboarding_flow",
                "name: Project Bootstrap And YAML Onboarding Flow",
                "purpose: Validate and bootstrap project-local YAML before first compile.",
                "simulation_sources:",
                "  - simulations/12_project_bootstrap_flow.md",
                "covers:",
                "  - project bootstrap",
                "entry_conditions:",
                "  - a repository exists",
                "task_flow:",
                "  - create project-local .ai structure",
                "required_subtasks:",
                "  - validate_project_yaml",
                "required_capabilities:",
                "  - yaml validate",
                "expected_tests:",
                "  - tests/integration/test_flow_yaml_contract_suite.py::test_flow_yaml_cases[14]",
                "known_limitations:",
                "  - project bootstrap remains policy-driven",
            ]
        ),
        encoding="utf-8",
    )

    asset = load_flow_yaml_asset(path)

    assert asset.id == "14_project_bootstrap_and_yaml_onboarding_flow"
    assert asset.simulation_sources == ["simulations/12_project_bootstrap_flow.md"]


def test_load_flow_yaml_asset_rejects_missing_required_keys(tmp_path: Path) -> None:
    path = tmp_path / "19_hook_expansion_compile_stage_flow.yaml"
    path.write_text(
        "\n".join(
            [
                "id: 19_hook_expansion_compile_stage_flow",
                "name: Hook Expansion Compile Stage Flow",
                "purpose: Describe hook expansion.",
                "simulation_sources:",
                "  - simulations/14_hook_expansion_flow.md",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(FlowAssetValidationError, match="invalid flow asset"):
        load_flow_yaml_asset(path)


def test_load_flow_yaml_asset_rejects_mismatched_filename_and_id(tmp_path: Path) -> None:
    path = tmp_path / "20_compile_failure_and_reattempt_flow.yaml"
    path.write_text(
        "\n".join(
            [
                "id: wrong_id",
                "name: Compile Failure And Reattempt Flow",
                "purpose: Retry compile after fixing a bad override.",
                "simulation_sources:",
                "  - simulations/13_compile_failure_flow.md",
                "covers:",
                "  - compile failure",
                "entry_conditions:",
                "  - a compile attempt failed",
                "task_flow:",
                "  - inspect compile failure",
                "required_subtasks:",
                "  - inspect_compile_failure",
                "required_capabilities:",
                "  - workflow compile-failures",
                "expected_tests:",
                "  - tests/integration/test_flow_yaml_contract_suite.py::test_flow_yaml_cases[20]",
                "known_limitations:",
                "  - compile retries reuse existing node version",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(FlowAssetValidationError, match="does not match filename stem"):
        load_flow_yaml_asset(path)


def test_load_flow_yaml_assets_loads_repo_assets_if_present() -> None:
    assets = load_flow_yaml_assets(REPO_ROOT / "flows")

    assert isinstance(assets, list)
    assert all(asset.id.endswith("_flow") for asset in assets)


def test_discover_flow_yaml_paths_only_returns_yaml_files() -> None:
    paths = discover_flow_yaml_paths(REPO_ROOT / "flows")

    assert all(path.suffix == ".yaml" for path in paths)
