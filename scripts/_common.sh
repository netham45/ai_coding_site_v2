#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
FRONTEND_DIR="${REPO_ROOT}/frontend"

run_in_repo_root() {
  cd "${REPO_ROOT}"
  "$@"
}

run_in_frontend() {
  cd "${FRONTEND_DIR}"
  "$@"
}
