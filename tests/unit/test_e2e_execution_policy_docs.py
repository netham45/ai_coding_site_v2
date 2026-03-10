from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO_ROOT / "notes" / "catalogs" / "checklists" / "e2e_execution_policy.md"


def test_e2e_execution_policy_defines_all_four_execution_tiers() -> None:
    text = POLICY_PATH.read_text(encoding="utf-8")

    for header in [
        "### Tier 1: Local Default Iteration",
        "### Tier 2: Standard CI",
        "### Tier 3: Gated Real E2E",
        "### Tier 4: Release-Readiness Review",
    ]:
        assert header in text

    assert "one database per test" in text
    assert "non-database resource constraints" in text
    assert "`requires_git`" in text
    assert "`requires_tmux`" in text
    assert "`requires_ai_provider`" in text


def test_authoritative_docs_link_to_execution_policy() -> None:
    paths = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "notes" / "catalogs" / "checklists" / "README.md",
        REPO_ROOT / "notes" / "catalogs" / "checklists" / "verification_command_catalog.md",
        REPO_ROOT / "notes" / "planning" / "implementation" / "full_real_end_to_end_flow_hardening_plan.md",
        REPO_ROOT / "notes" / "planning" / "implementation" / "project_development_flow_doctrine.md",
        REPO_ROOT / "plan" / "README.md",
        REPO_ROOT / "plan" / "checklists" / "04_test_coverage_and_release_readiness.md",
    ]

    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "notes/catalogs/checklists/e2e_execution_policy.md" in text, (
            f"{path.name} should link to the execution policy."
        )


def test_du04_plan_records_outputs_and_command() -> None:
    text = (
        REPO_ROOT / "plan" / "doc_updates" / "04_ci_e2e_execution_policy_and_release_alignment.md"
    ).read_text(encoding="utf-8")

    assert "## Current DU-04 Outputs" in text
    assert "notes/catalogs/checklists/e2e_execution_policy.md" in text
    assert "python3 -m pytest tests/unit/test_e2e_execution_policy_docs.py" in text


def test_release_readiness_checklist_points_to_canonical_policy_and_commands() -> None:
    text = (
        REPO_ROOT / "plan" / "checklists" / "04_test_coverage_and_release_readiness.md"
    ).read_text(encoding="utf-8")

    assert "notes/catalogs/checklists/verification_command_catalog.md" in text
    assert "notes/catalogs/checklists/e2e_execution_policy.md" in text
    assert "do not treat bounded or integration proof alone as `release_ready`" in text
