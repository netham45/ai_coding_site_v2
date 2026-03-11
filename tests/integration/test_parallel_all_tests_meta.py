from __future__ import annotations

import os
from pathlib import Path

import pytest

from tests.helpers.parallel_meta import collect_node_ids, run_parallel_child_pytest


def test_parallel_all_tests_meta_verifier() -> None:
    if os.environ.get("AICODING_META_TEST_CHILD") == "1":
        pytest.skip("Child pytest run ignores the meta-verifier recursion target.")

    if os.environ.get("AICODING_ENABLE_META_PARALLEL_TEST") != "1":
        pytest.skip("Set AICODING_ENABLE_META_PARALLEL_TEST=1 to run the parallel all-tests meta-verifier.")

    this_file = Path(__file__).resolve()
    all_collected = collect_node_ids()
    eligible_collected = collect_node_ids(ignored_path=this_file)

    assert all_collected, "Expected pytest to collect at least one test under tests/."
    assert eligible_collected, "Expected at least one eligible test after excluding the meta-verifier itself."

    child = run_parallel_child_pytest(ignored_path=this_file)

    assert child.returncode == 0, (
        "Parallel child pytest run failed.\n"
        f"stdout:\n{child.stdout}\n"
        f"stderr:\n{child.stderr}"
    )
