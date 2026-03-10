from __future__ import annotations

from aicoding.bootstrap import bootstrap_status, required_directories


def test_required_directories_exist() -> None:
    missing = [path for path in required_directories() if not path.exists()]
    assert missing == []


def test_bootstrap_status_reports_no_missing_directories() -> None:
    status = bootstrap_status()
    assert status["missing_directories"] == []
    assert status["project_root"]
    assert status["package_root"]

