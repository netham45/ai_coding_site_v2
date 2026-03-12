#!/usr/bin/env bash

set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/_common.sh"

PYTHONPATH=src run_in_repo_root uvicorn aicoding.daemon.app:create_app --factory --reload
