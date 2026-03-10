from pathlib import Path


FEATURE_DIR = Path(__file__).resolve().parents[2] / "plan" / "features"


def test_feature_plans_include_goal_rationale_and_scope() -> None:
    feature_files = sorted(path for path in FEATURE_DIR.glob("*.md") if path.name != "README.md")
    assert feature_files, "Expected at least one feature plan."

    for path in feature_files:
        text = path.read_text(encoding="utf-8")
        assert "## Goal\n" in text, f"{path.name} is missing a Goal section."
        assert "## Rationale\n" in text, f"{path.name} is missing a Rationale section."
        assert "## Related Features\n" in text, f"{path.name} is missing a Related Features section."
        assert "## Required Notes\n" in text, f"{path.name} is missing a Required Notes section."
        assert "## Scope\n" in text, f"{path.name} is missing a Scope section."
        assert (
            "- Rationale: " in text
        ), f"{path.name} is missing the rationale line in its Rationale section."
        assert (
            "- Reason for existence: " in text
        ), f"{path.name} is missing the reason-for-existence line in its Rationale section."
        assert (
            "Read these feature plans for implementation context and interaction boundaries:\n" in text
        ), f"{path.name} is missing the Related Features guidance line."
        assert "- `plan/features/" in text, f"{path.name} is missing feature-plan paths in Related Features."
        assert (
            "Read these note files before implementing or revising this phase:\n" in text
        ), f"{path.name} is missing the Required Notes guidance line."
        assert "- `notes/" in text, f"{path.name} is missing note paths in Required Notes."
