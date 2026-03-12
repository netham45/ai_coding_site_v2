#!/usr/bin/env bash

set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/_common.sh"

REVISION="${1:-head}"

PYTHONPATH=src run_in_repo_root python3 -m aicoding.cli.main admin db upgrade --revision "${REVISION}"
