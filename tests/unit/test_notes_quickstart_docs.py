from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_flows_readme_references_current_note_paths() -> None:
    text = (REPO_ROOT / "flows" / "README.md").read_text(encoding="utf-8")

    assert "notes/scenarios/journeys/common_user_journeys_analysis.md" in text
    assert "notes/specs/architecture/code_vs_yaml_delineation.md" in text
    assert "notes/catalogs/traceability/relevant_user_flow_inventory.yaml" in text
    assert "Python defines compilation" in text
    assert "`.yaml` flow assets for executable simulation-derived flow contracts" in text
    assert "C++ defines compilation" not in text


def test_getting_started_quickstart_mentions_current_entrypoint_and_query_loop() -> None:
    text = (
        REPO_ROOT / "notes" / "scenarios" / "walkthroughs" / "getting_started_hypothetical_task_guide.md"
    ).read_text(encoding="utf-8")

    assert "no longer an authoritative user/operator documentation surface" in text
    assert "docs/user/getting-started.md" in text
    assert "docs/operator/first-live-run.md" in text
    assert "docs/operator/inspect-state-and-blockers.md" in text
    assert "docs/runbooks/pause-resume-recovery.md" in text


def test_scenario_and_flow_pytest_plan_references_all_flow_docs_and_scenario_sources() -> None:
    text = (
        REPO_ROOT / "notes" / "planning" / "implementation" / "scenario_and_flow_pytest_plan.md"
    ).read_text(encoding="utf-8")

    assert "notes/scenarios/journeys/common_user_journeys_analysis.md" in text
    assert "notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md" in text
    assert "notes/scenarios/walkthroughs/hypothetical_plan_workthrough.md" in text
    assert "tests/integration/test_flow_contract_suite.py" in text
    for name in [
        "01_create_top_level_node_flow.md",
        "02_compile_or_recompile_workflow_flow.md",
        "03_materialize_and_schedule_children_flow.md",
        "04_manual_tree_edit_and_reconcile_flow.md",
        "05_admit_and_execute_node_run_flow.md",
        "06_inspect_state_and_blockers_flow.md",
        "07_pause_resume_and_recover_flow.md",
        "08_handle_failure_and_escalate_flow.md",
        "09_run_quality_gates_flow.md",
        "10_regenerate_and_rectify_flow.md",
        "11_finalize_and_merge_flow.md",
        "12_query_provenance_and_docs_flow.md",
        "13_human_gate_and_intervention_flow.md",
    ]:
        assert name in text


def test_readme_mentions_documentation_boundary_and_docs_tree() -> None:
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "docs/README.md" in text
    assert "## Documentation Boundary" in text
    assert "- `docs/` contains user-facing and operator-facing documentation artifacts" in text


def test_historical_plan_walkthrough_points_to_real_docs() -> None:
    text = (
        REPO_ROOT / "notes" / "scenarios" / "walkthroughs" / "hypothetical_plan_workthrough.md"
    ).read_text(encoding="utf-8")

    assert "historical simulation note" in text
    assert "docs/operator/tree-materialization-and-rebuild.md" in text
    assert "docs/operator/quality-provenance-and-finalize.md" in text
    assert "docs/runbooks/failure-escalation.md" in text


def test_flow_coverage_checklist_tracks_every_flow_and_the_new_suite() -> None:
    text = (
        REPO_ROOT / "notes" / "catalogs" / "audit" / "flow_coverage_checklist.md"
    ).read_text(encoding="utf-8")

    assert "tests/integration/test_flow_contract_suite.py" in text
    assert "scenario_and_flow_pytest_plan.md" in text
    assert "Top-level `scenarios/` directory exists" in text
    assert "Top-level `scenarios2/` directory exists" in text
    for name in [
        "01 Create Top-Level Node Flow",
        "02 Compile Or Recompile Workflow Flow",
        "03 Materialize And Schedule Children Flow",
        "04 Manual Tree Edit And Reconcile Flow",
        "05 Admit And Execute Node Run Flow",
        "06 Inspect State And Blockers Flow",
        "07 Pause Resume And Recover Flow",
        "08 Handle Failure And Escalate Flow",
        "09 Run Quality Gates Flow",
        "10 Regenerate And Rectify Flow",
        "11 Finalize And Merge Flow",
        "12 Query Provenance And Docs Flow",
        "13 Human Gate And Intervention Flow",
    ]:
        assert name in text


def test_per_flow_gap_remediation_plan_tracks_each_flow_and_git_gap() -> None:
    text = (
        REPO_ROOT / "notes" / "planning" / "implementation" / "per_flow_gap_remediation_plan.md"
    ).read_text(encoding="utf-8")

    assert "tests/integration/test_flow_contract_suite.py" in text
    assert "Phase 1: Baseline Flow Test Run" in text
    assert "Phase 2: Minimum Surface Closure" in text
    assert "Phase 3: Runtime Behavior Closure" in text
    assert "Phase 4: Audit And Recovery Closure" in text
    assert "Phase 5: Full Flow Confirmation" in text
    assert "Flow 11: Finalize And Merge" in text
    assert "live merge-children now performs real git fetch/merge" in text
    assert "Flow 04: Manual Tree Edit And Reconcile" in text
    assert "Flow 09: Run Quality Gates" in text
    assert "Flow 13: Human Gate And Intervention" in text
