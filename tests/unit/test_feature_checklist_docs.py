from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[2]
FEATURE_DIR = REPO_ROOT / "plan" / "features"
CHECKLIST_README_PATH = REPO_ROOT / "notes" / "catalogs" / "checklists" / "README.md"
STANDARD_PATH = REPO_ROOT / "notes" / "catalogs" / "checklists" / "feature_checklist_standard.md"
BACKFILL_PATH = REPO_ROOT / "notes" / "catalogs" / "checklists" / "feature_checklist_backfill.md"
INVENTORY_PATH = REPO_ROOT / "notes" / "catalogs" / "inventory" / "major_feature_inventory.md"


def test_checklist_standard_defines_allowed_statuses_and_command() -> None:
    text = STANDARD_PATH.read_text(encoding="utf-8")

    assert "notes/catalogs/checklists/README.md" in text
    for status in [
        "not_applicable",
        "planned",
        "in_progress",
        "implemented",
        "verified",
        "partial",
        "blocked",
        "deferred",
        "flow_complete",
        "release_ready",
    ]:
        assert f"`{status}`" in text

    assert "python3 -m pytest tests/unit/test_feature_checklist_docs.py" in text
    assert "feature_checklist_backfill.md" in text
    assert "user documentation status" in text
    assert "documentation surfaces affected" in text
    assert "notes status" in text


def test_feature_checklist_backfill_covers_every_feature_plan() -> None:
    text = BACKFILL_PATH.read_text(encoding="utf-8")

    feature_paths = sorted(path for path in FEATURE_DIR.glob("*.md") if path.name != "README.md")
    assert feature_paths, "Expected at least one feature plan."

    for path in feature_paths:
        rel = path.relative_to(REPO_ROOT).as_posix()
        assert f"`{rel}`" in text, f"Checklist backfill is missing {rel}."


def test_checklist_directory_readme_points_to_standard_and_backfill() -> None:
    text = CHECKLIST_README_PATH.read_text(encoding="utf-8")

    assert "feature_checklist_standard.md" in text
    assert "feature_checklist_backfill.md" in text
    assert "major_feature_inventory.md" in text


def test_checklist_docs_are_linked_from_inventory_and_readme_surfaces() -> None:
    inventory_text = INVENTORY_PATH.read_text(encoding="utf-8")
    doctrine_text = (
        REPO_ROOT / "notes" / "planning" / "implementation" / "project_development_flow_doctrine.md"
    ).read_text(encoding="utf-8")
    traceability_text = (
        REPO_ROOT / "notes" / "catalogs" / "traceability" / "spec_traceability_matrix.md"
    ).read_text(encoding="utf-8")
    readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for text in [inventory_text, doctrine_text, traceability_text, readme_text]:
        assert "notes/catalogs/checklists/feature_checklist_standard.md" in text
        assert "notes/catalogs/checklists/feature_checklist_backfill.md" in text


def test_backfill_entries_use_allowed_overall_statuses() -> None:
    text = BACKFILL_PATH.read_text(encoding="utf-8")

    overall_statuses = re.findall(r"Overall `([^`]+)`", text)
    assert overall_statuses, "Expected overall statuses in checklist backfill."
    assert set(overall_statuses) <= {
        "planned",
        "in_progress",
        "implemented",
        "partial",
        "verified",
        "flow_complete",
        "release_ready",
        "blocked",
        "deferred",
    }
