from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]


def has_git() -> bool:
    return shutil.which("git") is not None


def has_tmux() -> bool:
    return shutil.which("tmux") is not None


def has_ai_provider_credentials() -> bool:
    return any(key.startswith("OPENAI_") and value.strip() for key, value in os.environ.items())


def parallel_marker_expression() -> str | None:
    excluded: list[str] = []
    if not has_git():
        excluded.append("requires_git")
    if not has_tmux():
        excluded.append("requires_tmux")
    if not has_ai_provider_credentials():
        excluded.append("requires_ai_provider")
    if not excluded:
        return None
    return " and ".join(f"not {marker}" for marker in excluded)


def collect_node_ids(*, marker_expression: str | None = None, ignored_path: Path | None = None) -> list[str]:
    command = [sys.executable, "-m", "pytest", "tests", "--collect-only", "-q"]
    if marker_expression:
        command.extend(["-m", marker_expression])
    if ignored_path is not None:
        command.extend(["--ignore", str(ignored_path)])
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            "pytest collection failed for parallel meta-test.\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    return [line.strip() for line in completed.stdout.splitlines() if line.startswith("tests/")]


def run_parallel_child_pytest(*, ignored_path: Path, workers: str = "auto") -> subprocess.CompletedProcess[str]:
    marker_expression = parallel_marker_expression()
    command = [
        sys.executable,
        "-m",
        "pytest",
        "tests",
        "-n",
        workers,
        "--dist=loadfile",
        "-q",
        "--ignore",
        str(ignored_path),
    ]
    if marker_expression:
        command.extend(["-m", marker_expression])
    env = os.environ.copy()
    env["AICODING_META_TEST_CHILD"] = "1"
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
