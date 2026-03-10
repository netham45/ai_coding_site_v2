from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_flows_readme_references_current_note_paths() -> None:
    text = (REPO_ROOT / "flows" / "README.md").read_text(encoding="utf-8")

    assert "notes/scenarios/journeys/common_user_journeys_analysis.md" in text
    assert "notes/specs/architecture/code_vs_yaml_delineation.md" in text


def test_getting_started_quickstart_mentions_current_entrypoint_and_query_loop() -> None:
    text = (
        REPO_ROOT / "notes" / "scenarios" / "walkthroughs" / "getting_started_hypothetical_task_guide.md"
    ).read_text(encoding="utf-8")

    assert "workflow start \\" in text
    assert "--kind epic" in text
    assert "session show-current" in text
    assert "subtask prompt --node <node_id>" in text
    assert "workflow advance --node <node_id>" in text
    assert "epic` -> top-level kind" in text
