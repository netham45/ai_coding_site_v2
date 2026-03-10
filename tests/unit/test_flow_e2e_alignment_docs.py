from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_flow_coverage_checklist_has_bounded_vs_real_e2e_summary() -> None:
    text = (
        REPO_ROOT / "notes" / "catalogs" / "audit" / "flow_coverage_checklist.md"
    ).read_text(encoding="utf-8")

    assert "## Flow Status Summary" in text
    assert "| Flow | Bounded proof status | Real E2E target | Real E2E completion |" in text
    assert "`flow_complete` in the bounded column means the current bounded flow-contract suite passes" in text
    assert "tests/e2e/test_flow_01_create_top_level_node_real.py" in text
    assert "tests/e2e/test_flow_09_run_quality_gates_real.py" in text


def test_per_flow_gap_plan_explains_its_labels_are_bounded_only() -> None:
    text = (
        REPO_ROOT / "notes" / "planning" / "implementation" / "per_flow_gap_remediation_plan.md"
    ).read_text(encoding="utf-8")

    assert "the `full`, `partial`, and `deferred_heavy` labels in this document describe bounded flow-contract support only" in text
    assert "mark the bounded flow-contract layer `flow_complete`" in text


def test_simulation_inventory_and_e2e_matrix_explain_their_boundaries() -> None:
    simulation_text = (
        REPO_ROOT / "notes" / "catalogs" / "traceability" / "simulation_flow_union_inventory.md"
    ).read_text(encoding="utf-8")
    matrix_text = (
        REPO_ROOT / "plan" / "e2e_tests" / "06_e2e_feature_matrix.md"
    ).read_text(encoding="utf-8")

    assert "simulations and simulation-derived YAML flow assets are planning and bounded-proof artifacts" in simulation_text
    assert "this matrix assigns real-E2E targets only" in matrix_text
    assert "it does not claim that the named suite already exists or is already passing" in matrix_text


def test_du03_plan_records_outputs_and_command() -> None:
    text = (
        REPO_ROOT / "plan" / "doc_updates" / "03_flow_traceability_and_e2e_status_alignment.md"
    ).read_text(encoding="utf-8")

    assert "## Current DU-03 Outputs" in text
    assert "notes/catalogs/audit/flow_coverage_checklist.md" in text
    assert "python3 -m pytest tests/unit/test_flow_e2e_alignment_docs.py" in text


def test_feature_checklist_backfill_reflects_flow05_real_e2e_checkpoint() -> None:
    text = (
        REPO_ROOT / "notes" / "catalogs" / "checklists" / "feature_checklist_backfill.md"
    ).read_text(encoding="utf-8")

    assert "tests/e2e/test_flow_05_admit_and_execute_node_run_real.py" in text
    assert "The repo now has a real Flow 05 checkpoint for the shipped durable run-control loop" in text
