from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = REPO_ROOT / "notes" / "catalogs" / "checklists" / "verification_command_catalog.md"


def test_verification_command_catalog_defines_current_command_families() -> None:
    text = CATALOG_PATH.read_text(encoding="utf-8")

    for snippet in [
        "PYTHONPATH=src python3 -m aicoding.cli.main admin db ping",
        "PYTHONPATH=src python3 -m aicoding.cli.main admin db heads",
        "PYTHONPATH=src python3 -m aicoding.cli.main admin db upgrade",
        "PYTHONPATH=src python3 -m aicoding.cli.main admin db check-schema",
        "PYTHONPATH=src python3 -m pytest tests/unit",
        "PYTHONPATH=src python3 -m pytest tests/integration",
        "PYTHONPATH=src python3 -m pytest tests/integration/test_flow_contract_suite.py -q",
        "PYTHONPATH=src python3 -m pytest tests/integration/test_flow_yaml_contract_suite.py -q",
        "PYTHONPATH=src python3 -m pytest tests/performance/test_harness.py -q",
        "PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_01_create_top_level_node_real.py -q",
        "PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_04_manual_tree_edit_and_reconcile_real.py -q",
    ]:
        assert snippet in text
    assert "`e2e_bringup`" in text


def test_authoritative_docs_link_to_verification_command_catalog() -> None:
    paths = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "notes" / "catalogs" / "audit" / "flow_coverage_checklist.md",
        REPO_ROOT / "notes" / "catalogs" / "audit" / "auditability_checklist.md",
        REPO_ROOT / "notes" / "catalogs" / "traceability" / "spec_traceability_matrix.md",
        REPO_ROOT / "notes" / "planning" / "implementation" / "scenario_and_flow_pytest_plan.md",
        REPO_ROOT / "notes" / "planning" / "implementation" / "full_real_end_to_end_flow_hardening_plan.md",
        REPO_ROOT / "plan" / "update_tests" / "01_batch_execution_groups.md",
    ]

    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "notes/catalogs/checklists/verification_command_catalog.md" in text, (
            f"{path.name} should link to the verification command catalog."
        )


def test_du02_plan_records_its_current_outputs_and_command() -> None:
    text = (
        REPO_ROOT / "plan" / "doc_updates" / "02_status_vocabulary_and_command_normalization.md"
    ).read_text(encoding="utf-8")

    assert "## Current DU-02 Outputs" in text
    assert "notes/catalogs/checklists/verification_command_catalog.md" in text
    assert "PYTHONPATH=src python3 -m pytest tests/unit/test_verification_command_docs.py" in text


def test_traceability_matrix_explains_covered_is_not_completion_claim() -> None:
    text = (
        REPO_ROOT / "notes" / "catalogs" / "traceability" / "spec_traceability_matrix.md"
    ).read_text(encoding="utf-8")

    assert "`covered` and `partially_covered` in this document describe specification and artifact coverage only." in text
    assert "They do not mean a feature is `verified`, `flow_complete`, or `release_ready`." in text


def test_planning_inventory_docs_explain_their_completion_language_scope() -> None:
    paths = [
        REPO_ROOT / "notes" / "catalogs" / "traceability" / "action_automation_matrix.md",
        REPO_ROOT / "notes" / "catalogs" / "inventory" / "yaml_inventory_v2.md",
        REPO_ROOT / "notes" / "catalogs" / "inventory" / "default_yaml_library_plan.md",
        REPO_ROOT / "plan" / "update_tests" / "00_raise_existing_tests_to_doctrine_level.md",
    ]

    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "Interpretation rule:" in text, f"{path.name} should scope its completion language."
