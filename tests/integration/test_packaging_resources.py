from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_built_wheel_includes_canonical_packaged_resources(tmp_path: Path) -> None:
    wheel_dir = tmp_path / "wheelhouse"
    wheel_dir.mkdir(parents=True, exist_ok=True)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--wheel-dir",
            str(wheel_dir),
            ".",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr

    wheels = sorted(wheel_dir.glob("*.whl"))
    assert wheels, "Expected pip wheel to produce a wheel artifact."

    with ZipFile(wheels[0]) as archive:
        names = set(archive.namelist())

    assert "aicoding/resources/yaml/builtin/system-yaml/policies/default_runtime_policy.yaml" in names
    assert "aicoding/resources/prompts/packs/default/recovery/idle_nudge.md" in names
