from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_user_documentation_system_is_declared_in_doctrine_and_contract() -> None:
    agents_text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    contract_text = (
        REPO_ROOT / "notes" / "specs" / "product" / "user_documentation_contract.md"
    ).read_text(encoding="utf-8")

    assert "### 7. User Documentation" in agents_text
    assert "`docs/` are consumer-facing user and operator documentation artifacts" in agents_text
    assert "## Required Plan And Checklist Linkage" in contract_text
    assert "Task plans created or materially revised on or after 2026-03-13" in contract_text


def test_docs_tree_and_historical_scenario_surfaces_exist() -> None:
    for relative in [
        "docs/README.md",
        "docs/user/README.md",
        "docs/operator/README.md",
        "docs/reference/README.md",
        "docs/runbooks/README.md",
        "notes/scenarios/journeys/common_user_journeys_analysis.md",
        "notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md",
        "notes/scenarios/walkthroughs/hypothetical_plan_workthrough.md",
    ]:
        assert (REPO_ROOT / relative).is_file(), f"Missing documentation surface {relative}"


def test_documentation_family_and_policy_are_authoritative() -> None:
    inventory_text = (
        REPO_ROOT / "notes" / "catalogs" / "checklists" / "authoritative_document_family_inventory.md"
    ).read_text(encoding="utf-8")
    rulebook_text = (
        REPO_ROOT / "notes" / "catalogs" / "checklists" / "document_schema_rulebook.md"
    ).read_text(encoding="utf-8")
    policy_text = (
        REPO_ROOT / "notes" / "catalogs" / "checklists" / "document_schema_test_policy.md"
    ).read_text(encoding="utf-8")

    assert "DF-20 | User/operator documentation family | yes" in inventory_text
    assert "### User Documentation Family" in rulebook_text
    assert "historical scenario walkthroughs under `notes/scenarios/`" in rulebook_text
    assert "documentation-governance changes" in policy_text
    assert "tests/unit/test_user_documentation_governance_docs.py" in policy_text


def test_new_task_plans_record_documentation_sections() -> None:
    task_dir = REPO_ROOT / "plan" / "tasks"
    for path in sorted(task_dir.glob("2026-03-13_*.md")):
        text = path.read_text(encoding="utf-8")
        assert "## Documentation Impact\n" in text, f"{path.name} missing Documentation Impact"
        assert "## Documentation Verification\n" in text, f"{path.name} missing Documentation Verification"


def test_relevant_user_flow_inventory_records_documentation_fields() -> None:
    text = (
        REPO_ROOT / "notes" / "catalogs" / "traceability" / "relevant_user_flow_inventory.yaml"
    ).read_text(encoding="utf-8")

    assert "user_documentation: affected" in text
    assert "documentation:" in text
    assert "surfaces:" in text
    assert "docs/README.md" in text
