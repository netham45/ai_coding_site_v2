from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKLISTS_DIR = REPO_ROOT / "notes" / "catalogs" / "checklists"
DOC_SCHEMA_PLAN_DIR = REPO_ROOT / "plan" / "doc_schemas"
SETUP_PLAN_DIR = REPO_ROOT / "plan" / "setup"
WEB_PLAN_DIR = REPO_ROOT / "plan" / "web"
WEB_SETUP_PLAN_DIR = WEB_PLAN_DIR / "setup"
WEB_FEATURE_PLAN_DIR = WEB_PLAN_DIR / "features"
WEB_VERIFICATION_PLAN_DIR = WEB_PLAN_DIR / "verification"
TASK_PLAN_DIR = REPO_ROOT / "plan" / "tasks"
CHECKLIST_PLAN_DIR = REPO_ROOT / "plan" / "checklists"
E2E_PLAN_DIR = REPO_ROOT / "plan" / "e2e_tests"
UPDATE_TEST_PLAN_DIR = REPO_ROOT / "plan" / "update_tests"
DOC_UPDATE_PLAN_DIR = REPO_ROOT / "plan" / "doc_updates"
LOG_DIR = REPO_ROOT / "notes" / "logs"


def _section_lines(text: str, heading: str) -> list[str]:
    marker = f"## {heading}\n"
    assert marker in text, f"Missing section {heading!r}."
    section = text.split(marker, 1)[1]
    next_heading = section.find("\n## ")
    if next_heading != -1:
        section = section[:next_heading]
    return [line.strip() for line in section.splitlines() if line.strip()]


def test_authoritative_document_family_inventory_lists_key_families() -> None:
    text = (CHECKLISTS_DIR / "authoritative_document_family_inventory.md").read_text(encoding="utf-8")

    for family_id in ["DF-03", "DF-04", "DF-08", "DF-09", "DF-10", "DF-14", "DF-15", "DF-16", "DF-18"]:
        assert family_id in text
    assert "Task plans | yes | `plan/tasks/*.md`" in text
    assert "Development logs and operational logs | yes" in text


def test_document_schema_rulebook_covers_plan_flow_and_log_families() -> None:
    text = (CHECKLISTS_DIR / "document_schema_rulebook.md").read_text(encoding="utf-8")

    for heading in [
        "### Plan And Checklist Families",
        "### Feature Checklist Family",
        "### Flow, Traceability, And E2E Families",
        "### Traceability Catalog Family",
        "### Audit Checklist Family",
        "### Command And Execution Policy Families",
        "### Operational Log Family",
    ]:
        assert heading in text

    assert "setup plans must include:" in text
    assert "verification checklists must include:" in text
    assert "standard richer plan schema families must include:" in text
    assert "task plans must additionally include:" in text
    assert "log files must live under a structured subdirectory" in text
    assert "coverage, gap, and planning statuses must be scoped explicitly" in text
    assert "audit/review-only status values must be scoped explicitly" in text


def test_document_schema_test_policy_defines_core_suite_and_adoption_rules() -> None:
    text = (CHECKLISTS_DIR / "document_schema_test_policy.md").read_text(encoding="utf-8")

    assert "## Canonical Commands" in text
    assert "tests/unit/test_document_schema_docs.py" in text
    assert "## Adoption Rules" in text
    assert "## Failure Triage" in text


def test_family_readmes_link_to_document_schema_surfaces() -> None:
    shared_readmes = [
        REPO_ROOT / "plan" / "setup" / "README.md",
        REPO_ROOT / "plan" / "tasks" / "README.md",
        REPO_ROOT / "plan" / "doc_schemas" / "README.md",
        REPO_ROOT / "plan" / "web" / "README.md",
        REPO_ROOT / "plan" / "web" / "setup" / "README.md",
        REPO_ROOT / "plan" / "web" / "features" / "README.md",
        REPO_ROOT / "plan" / "web" / "verification" / "README.md",
    ]

    for path in shared_readmes:
        text = path.read_text(encoding="utf-8")
        assert "document_schema_rulebook.md" in text or "authoritative_document_family_inventory.md" in text
        assert "document_schema_test_policy.md" in text

    checklist_readme = (REPO_ROOT / "plan" / "checklists" / "README.md").read_text(encoding="utf-8")
    assert "document_schema_rulebook.md" in checklist_readme
    assert "document_schema_test_policy.md" in checklist_readme
    assert "feature_checklist_standard.md" in checklist_readme
    assert "verification_command_catalog.md" in checklist_readme
    assert "e2e_execution_policy.md" in checklist_readme

    e2e_readme = (REPO_ROOT / "plan" / "e2e_tests" / "README.md").read_text(encoding="utf-8")
    assert "document_schema_rulebook.md" in e2e_readme
    assert "document_schema_test_policy.md" in e2e_readme
    assert "verification_command_catalog.md" in e2e_readme
    assert "e2e_execution_policy.md" in e2e_readme


def test_doc_schema_plans_record_outputs_and_commands() -> None:
    plan_files = sorted(path for path in DOC_SCHEMA_PLAN_DIR.glob("*.md") if path.name != "README.md")
    assert plan_files, "Expected doc-schema plan files."

    for path in plan_files:
        text = path.read_text(encoding="utf-8")
        assert "## Current DS-" in text, f"{path.name} should record its current outputs."
        assert "## Canonical Verification Command" in text, f"{path.name} should record a canonical verification command."


def test_setup_plans_follow_lightweight_schema() -> None:
    plan_files = sorted(path for path in SETUP_PLAN_DIR.glob("*.md") if path.name != "README.md")
    assert plan_files, "Expected setup plan files."

    for path in plan_files:
        text = path.read_text(encoding="utf-8")
        assert "## Goal\n" in text, f"{path.name} is missing a Goal section."
        assert "## Scope\n" in text, f"{path.name} is missing a Scope section."
        assert "## Exit Criteria\n" in text, f"{path.name} is missing an Exit Criteria section."
        for system in ["Database:", "CLI:", "Daemon:", "YAML:", "Prompts:", "Tests:", "Performance:", "Notes:"]:
            assert system in text, f"{path.name} should cover {system.rstrip(':')} in Scope."

    web_setup_files = sorted(path for path in WEB_SETUP_PLAN_DIR.glob("*.md") if path.name != "README.md")
    assert web_setup_files, "Expected web setup plan files."

    for path in web_setup_files:
        text = path.read_text(encoding="utf-8")
        assert "## Goal\n" in text, f"{path.name} is missing a Goal section."
        assert "## Scope\n" in text, f"{path.name} is missing a Scope section."
        assert "## Exit Criteria\n" in text, f"{path.name} is missing an Exit Criteria section."
        for system in ["Database:", "CLI:", "Daemon:", "YAML:", "Prompts:", "Tests:", "Performance:", "Notes:"]:
            assert system in text, f"{path.name} should cover {system.rstrip(':')} in Scope."


def test_task_plan_readme_and_family_exist() -> None:
    assert TASK_PLAN_DIR.exists()
    readme_text = (TASK_PLAN_DIR / "README.md").read_text(encoding="utf-8")
    assert "document_schema_rulebook.md" in readme_text
    assert "document_schema_test_policy.md" in readme_text
    assert "standard richer plan schema" in readme_text


def test_verification_checklists_follow_checklist_schema() -> None:
    checklist_files = sorted(path for path in CHECKLIST_PLAN_DIR.glob("*.md") if path.name != "README.md")
    assert checklist_files, "Expected checklist files."

    for path in checklist_files:
        text = path.read_text(encoding="utf-8")
        assert "## Goal\n" in text, f"{path.name} is missing a Goal section."
        assert "## Verify\n" in text, f"{path.name} is missing a Verify section."
        assert "## Tests\n" in text, f"{path.name} is missing a Tests section."
        assert "## Notes\n" in text, f"{path.name} is missing a Notes section."

    release_readiness_text = (CHECKLIST_PLAN_DIR / "04_test_coverage_and_release_readiness.md").read_text(encoding="utf-8")
    for required_ref in [
        "feature_checklist_standard.md",
        "verification_command_catalog.md",
        "e2e_execution_policy.md",
    ]:
        assert required_ref in release_readiness_text


def test_e2e_and_update_test_plans_follow_richer_schema() -> None:
    families = [
        E2E_PLAN_DIR,
        UPDATE_TEST_PLAN_DIR,
        DOC_UPDATE_PLAN_DIR,
        DOC_SCHEMA_PLAN_DIR,
    ]

    for family_dir in families:
        files = sorted(path for path in family_dir.glob("*.md") if path.name != "README.md")
        assert files, f"Expected plan files under {family_dir}."

        for path in files:
            text = path.read_text(encoding="utf-8")
            assert "## Goal\n" in text, f"{path.name} is missing a Goal section."
            assert "## Rationale\n" in text, f"{path.name} is missing a Rationale section."
            assert "## Related Features\n" in text, f"{path.name} is missing a Related Features section."
            assert "## Required Notes\n" in text, f"{path.name} is missing a Required Notes section."
            assert "## Scope\n" in text, f"{path.name} is missing a Scope section."
            assert "- Rationale: " in text, f"{path.name} is missing the rationale line."
            assert "- Reason for existence: " in text, f"{path.name} is missing the reason-for-existence line."
            assert any(
                line.startswith("- `") for line in _section_lines(text, "Related Features")
            ), f"{path.name} should include explicit references in Related Features."
            assert any(
                line.startswith("- `") for line in _section_lines(text, "Required Notes")
            ), f"{path.name} should include explicit references in Required Notes."

            if family_dir == E2E_PLAN_DIR:
                assert "verification_command_catalog.md" in text, (
                    f"{path.name} should point to the canonical command catalog."
                )
                assert "e2e_execution_policy.md" in text, (
                    f"{path.name} should point to the E2E execution policy."
                )

    for family_dir in [WEB_FEATURE_PLAN_DIR, WEB_VERIFICATION_PLAN_DIR]:
        files = sorted(path for path in family_dir.glob("*.md") if path.name != "README.md")
        assert files, f"Expected plan files under {family_dir}."

        for path in files:
            text = path.read_text(encoding="utf-8")
            assert "## Goal\n" in text, f"{path.name} is missing a Goal section."
            assert "## Rationale\n" in text, f"{path.name} is missing a Rationale section."
            assert "## Related Features\n" in text, f"{path.name} is missing a Related Features section."
            assert "## Required Notes\n" in text, f"{path.name} is missing a Required Notes section."
            assert "## Scope\n" in text, f"{path.name} is missing a Scope section."
            assert "- Rationale: " in text, f"{path.name} is missing the rationale line."
            assert "- Reason for existence: " in text, f"{path.name} is missing the reason-for-existence line."
            assert any(
                line.startswith("- `") for line in _section_lines(text, "Related Features")
            ), f"{path.name} should include explicit references in Related Features."
            assert any(
                line.startswith("- `") for line in _section_lines(text, "Required Notes")
            ), f"{path.name} should include explicit references in Required Notes."


def test_no_notes_logs_directory_is_present_while_log_family_is_deferred() -> None:
    inventory_text = (CHECKLISTS_DIR / "authoritative_document_family_inventory.md").read_text(encoding="utf-8")
    assert LOG_DIR.exists()
    assert "DF-16 | Development logs and operational logs | yes" in inventory_text


def test_development_logs_follow_required_schema() -> None:
    log_files = sorted(LOG_DIR.glob("*/*.md"))
    assert log_files, "Expected adopted development logs."

    allowed_statuses = {
        "started",
        "in_progress",
        "blocked",
        "changed_plan",
        "bounded_tests_passed",
        "e2e_pending",
        "e2e_passed",
        "partial",
        "deferred",
        "complete",
    }

    for path in log_files:
        text = path.read_text(encoding="utf-8")
        assert "## Entry " in text, f"{path.name} should include at least one log entry."
        for required_field in [
            "Timestamp:",
            "Task ID:",
            "Task title:",
            "Status:",
            "Affected systems:",
            "Summary:",
            "Plans and notes consulted:",
            "Commands and tests run:",
            "Result:",
            "Next step:",
        ]:
            assert required_field in text, f"{path.name} is missing {required_field}"
        assert "`plan/tasks/" in text, f"{path.name} should cite its governing task plan."
        assert any(f"Status: {status}" in text for status in allowed_statuses), (
            f"{path.name} should use an allowed development-log status."
        )


def test_traceability_and_audit_note_families_define_status_scope() -> None:
    spec_traceability_text = (
        REPO_ROOT / "notes" / "catalogs" / "traceability" / "spec_traceability_matrix.md"
    ).read_text(encoding="utf-8")
    assert "Interpretation rule:" in spec_traceability_text
    assert "They do not mean a feature is `verified`, `flow_complete`, or `release_ready`." in spec_traceability_text
    assert "feature_checklist_backfill.md" in spec_traceability_text
    assert "verification_command_catalog.md" in spec_traceability_text

    simulation_union_text = (
        REPO_ROOT / "notes" / "catalogs" / "traceability" / "simulation_flow_union_inventory.md"
    ).read_text(encoding="utf-8")
    assert "Interpretation rule:" in simulation_union_text
    assert "they do not count as real-E2E completion by themselves" in simulation_union_text
    assert "flow_coverage_checklist.md" in simulation_union_text
    assert "feature_checklist_backfill.md" in simulation_union_text

    action_matrix_text = (
        REPO_ROOT / "notes" / "catalogs" / "traceability" / "action_automation_matrix.md"
    ).read_text(encoding="utf-8")
    assert "Interpretation rule:" in action_matrix_text
    assert "it does not mean the repository or feature set is `verified`, `flow_complete`, or `release_ready`" in action_matrix_text

    cross_spec_text = (
        REPO_ROOT / "notes" / "catalogs" / "traceability" / "cross_spec_gap_matrix.md"
    ).read_text(encoding="utf-8")
    assert "Interpretation rule:" in cross_spec_text
    assert "spec-review and implementation-planning statuses only" in cross_spec_text
    assert "feature_checklist_backfill.md" in cross_spec_text
    assert "verification_command_catalog.md" in cross_spec_text

    auditability_text = (
        REPO_ROOT / "notes" / "catalogs" / "audit" / "auditability_checklist.md"
    ).read_text(encoding="utf-8")
    assert "Status language rule:" in auditability_text
    assert "use the checklist layer for `implemented`, `verified`, `flow_complete`, and `release_ready` claims" in auditability_text
    assert "verification_command_catalog.md" in auditability_text

    flow_coverage_text = (
        REPO_ROOT / "notes" / "catalogs" / "audit" / "flow_coverage_checklist.md"
    ).read_text(encoding="utf-8")
    assert "Status vocabulary rule:" in flow_coverage_text
    assert "Interpretation rule:" in flow_coverage_text
    assert "## Flow Status Summary" in flow_coverage_text
    assert "| Flow | Bounded proof status | Real E2E target | Real E2E completion |" in flow_coverage_text

    yaml_builtins_text = (
        REPO_ROOT / "notes" / "catalogs" / "audit" / "yaml_builtins_checklist.md"
    ).read_text(encoding="utf-8")
    assert "Interpretation rule:" in yaml_builtins_text
    assert "not the canonical implementation or proving surface" in yaml_builtins_text
    assert "feature_checklist_backfill.md" in yaml_builtins_text
    assert "verification_command_catalog.md" in yaml_builtins_text
