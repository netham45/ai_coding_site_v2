#!/usr/bin/env bash

set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/_common.sh"

REVISION="${1:-base}"

PYTHONPATH=src run_in_repo_root python3 -m aicoding.cli.main admin db downgrade --revision "${REVISION}"
