#!/usr/bin/env bash

set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/_common.sh"

run_in_repo_root python3 -m pytest tests/e2e -m "e2e_bringup"
