from __future__ import annotations

import pytest

from tests.helpers.cli import CLIResult, invoke_cli


@pytest.fixture
def cli_runner(capsys):
    def run_cli(args: list[str]) -> CLIResult:
        return invoke_cli(args, capsys)

    return run_cli
