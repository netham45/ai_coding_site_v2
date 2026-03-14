from pathlib import Path


TASK_DIR = Path(__file__).resolve().parents[2] / "plan" / "tasks"


def test_task_plans_follow_standard_schema_with_task_sections() -> None:
    task_files = sorted(path for path in TASK_DIR.glob("*.md") if path.name != "README.md")
    assert task_files, "Expected at least one task plan."

    for path in task_files:
        text = path.read_text(encoding="utf-8")
        assert "## Goal\n" in text, f"{path.name} is missing a Goal section."
        assert "## Rationale\n" in text, f"{path.name} is missing a Rationale section."
        assert "## Related Features\n" in text, f"{path.name} is missing a Related Features section."
        assert "## Required Notes\n" in text, f"{path.name} is missing a Required Notes section."
        assert "## Scope\n" in text, f"{path.name} is missing a Scope section."
        assert "## Verification\n" in text, f"{path.name} is missing a Verification section."
        assert "## Exit Criteria\n" in text, f"{path.name} is missing an Exit Criteria section."
        assert "- Rationale: " in text, f"{path.name} is missing the rationale line."
        assert "- Reason for existence: " in text, f"{path.name} is missing the reason-for-existence line."
        assert (
            "Read these feature plans for implementation context and interaction boundaries:\n" in text
        ), f"{path.name} is missing the Related Features guidance line."
        assert "- `plan/features/" in text, f"{path.name} should include feature-plan references."
        assert (
            "Read these note files before implementing or revising this phase:\n" in text
        ), f"{path.name} is missing the Required Notes guidance line."
        assert "- `notes/" in text or "- `AGENTS.md`" in text, f"{path.name} should include note references."

        for system in ["Database:", "CLI:", "Daemon:", "YAML:", "Prompts:", "Tests:", "Performance:", "Notes:"]:
            assert system in text, f"{path.name} should cover {system.rstrip(':')} in Scope."

        if path.name >= "2026-03-13_":
            assert "## Documentation Impact\n" in text, (
                f"{path.name} is missing a Documentation Impact section."
            )
            assert "## Documentation Verification\n" in text, (
                f"{path.name} is missing a Documentation Verification section."
            )
