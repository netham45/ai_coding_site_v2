from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent.parent

EXPECTED_DIRECTORIES = (
    "src/aicoding/cli",
    "src/aicoding/daemon",
    "src/aicoding/db",
    "src/aicoding/resources/yaml/builtin",
    "src/aicoding/resources/yaml/project",
    "src/aicoding/resources/yaml/overrides",
    "src/aicoding/resources/yaml/schemas",
    "src/aicoding/resources/prompts/layouts",
    "src/aicoding/resources/prompts/execution",
    "src/aicoding/resources/prompts/recovery",
    "src/aicoding/resources/prompts/quality",
    "tests/unit",
    "tests/integration",
    "tests/performance",
    "tests/fixtures",
    "tests/factories",
    "alembic/versions",
)


def required_directories() -> list[Path]:
    return [PROJECT_ROOT / relative_path for relative_path in EXPECTED_DIRECTORIES]


def bootstrap_status() -> dict[str, object]:
    directories = required_directories()
    missing = [str(path.relative_to(PROJECT_ROOT)) for path in directories if not path.exists()]
    return {
        "project_root": str(PROJECT_ROOT),
        "package_root": str(PACKAGE_ROOT),
        "missing_directories": missing,
    }

