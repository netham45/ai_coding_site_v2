from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

QUARANTINED_FILES = [
    REPO_ROOT / "tests" / "e2e" / "test_flow_21_child_session_round_trip_and_mergeback_real.py",
    REPO_ROOT / "tests" / "e2e" / "test_e2e_automated_full_tree_cat_runtime_real.py",
    REPO_ROOT / "tests" / "e2e" / "test_e2e_full_epic_tree_runtime_real.py",
    REPO_ROOT / "tests" / "e2e" / "test_e2e_incremental_parent_merge_real.py",
    REPO_ROOT / "tests" / "e2e" / "test_e2e_rebuild_cutover_coordination_real.py",
    REPO_ROOT / "tests" / "e2e" / "test_tmux_codex_idle_nudge_real.py",
]


def test_quarantined_e2e_files_carry_e2e_bringup_marker() -> None:
    for path in QUARANTINED_FILES:
        text = path.read_text(encoding="utf-8")
        assert "e2e_bringup" in text, f"{path.name} must carry the e2e_bringup marker while quarantined."
