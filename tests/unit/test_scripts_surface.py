from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"


def test_root_shell_scripts_exist() -> None:
    expected = [
        "_common.sh",
        "downgrade-db.sh",
        "rebuild.sh",
        "reset-db.sh",
        "run-node-dev.sh",
        "run-server.sh",
        "test-unit.sh",
        "test-integration.sh",
        "test-e2e.sh",
        "test-all.sh",
        "upgrade-db.sh",
    ]

    for name in expected:
        assert (SCRIPTS_DIR / name).exists(), f"Missing script: {name}"


def test_root_shell_scripts_wrap_current_canonical_commands() -> None:
    downgrade_db = (SCRIPTS_DIR / "downgrade-db.sh").read_text(encoding="utf-8")
    rebuild = (SCRIPTS_DIR / "rebuild.sh").read_text(encoding="utf-8")
    reset_db = (SCRIPTS_DIR / "reset-db.sh").read_text(encoding="utf-8")
    run_node_dev = (SCRIPTS_DIR / "run-node-dev.sh").read_text(encoding="utf-8")
    run_server = (SCRIPTS_DIR / "run-server.sh").read_text(encoding="utf-8")
    test_unit = (SCRIPTS_DIR / "test-unit.sh").read_text(encoding="utf-8")
    test_integration = (SCRIPTS_DIR / "test-integration.sh").read_text(encoding="utf-8")
    test_e2e = (SCRIPTS_DIR / "test-e2e.sh").read_text(encoding="utf-8")
    test_all = (SCRIPTS_DIR / "test-all.sh").read_text(encoding="utf-8")
    upgrade_db = (SCRIPTS_DIR / "upgrade-db.sh").read_text(encoding="utf-8")

    assert 'REVISION="${1:-base}"' in downgrade_db
    assert "python3 -m aicoding.cli.main admin db downgrade --revision" in downgrade_db
    assert "npm run build" in rebuild
    assert "reset_public_schema" in reset_db
    assert "python3 -m aicoding.cli.main admin db ping" in reset_db
    assert "python3 -m aicoding.cli.main admin db heads" in reset_db
    assert "python3 -m aicoding.cli.main admin db upgrade" in reset_db
    assert "python3 -m aicoding.cli.main admin db check-schema" in reset_db
    assert "Type RESET to continue" in reset_db
    assert "npm run dev" in run_node_dev
    assert "uvicorn aicoding.daemon.app:create_app --factory --reload" in run_server
    assert "python3 -m pytest tests/unit" in test_unit
    assert "npm run test:unit" in test_unit
    assert "python3 -m pytest tests/integration" in test_integration
    assert "python3 -m pytest tests/e2e" in test_e2e
    assert "npm run test:e2e" in test_e2e
    assert "test-unit.sh" in test_all
    assert "test-integration.sh" in test_all
    assert "test-e2e.sh" in test_all
    assert 'REVISION="${1:-head}"' in upgrade_db
    assert "python3 -m aicoding.cli.main admin db upgrade --revision" in upgrade_db


def test_readmes_and_catalog_reference_root_scripts() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    frontend_readme = (REPO_ROOT / "frontend" / "README.md").read_text(encoding="utf-8")
    command_catalog = (
        REPO_ROOT / "notes" / "catalogs" / "checklists" / "verification_command_catalog.md"
    ).read_text(encoding="utf-8")

    for text in [readme, frontend_readme, command_catalog]:
        assert "scripts/downgrade-db.sh" in text
        assert "scripts/rebuild.sh" in text
        assert "scripts/reset-db.sh" in text
        assert "scripts/run-node-dev.sh" in text
        assert "scripts/run-server.sh" in text
        assert "scripts/test-unit.sh" in text
        assert "scripts/test-integration.sh" in text
        assert "scripts/test-e2e.sh" in text
        assert "scripts/test-all.sh" in text
        assert "scripts/upgrade-db.sh" in text
