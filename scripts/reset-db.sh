#!/usr/bin/env bash

set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/_common.sh"

usage() {
  cat <<'EOF'
Usage: ./scripts/reset-db.sh [--yes]

Wipe the PostgreSQL database configured by AICODING_DATABASE_URL/.env,
then rebuild it using the documented bootstrap commands:
  - admin db ping
  - admin db heads
  - admin db upgrade
  - admin db check-schema

This is destructive.
EOF
}

require_confirmation() {
  if [[ "${1:-}" == "--yes" ]]; then
    return 0
  fi

  if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    usage
    exit 0
  fi

  if [[ -n "${1:-}" ]]; then
    echo "Unknown argument: ${1}" >&2
    usage >&2
    exit 1
  fi

  if [[ ! -t 0 ]]; then
    echo "Refusing to reset the configured database without an interactive confirmation or --yes." >&2
    exit 1
  fi

  local database_name
  database_name="$(
    cd "${REPO_ROOT}" &&
      python3 - <<'PY'
from sqlalchemy.engine import make_url
from aicoding.config import get_settings

print(make_url(get_settings().database_url).database or "<unknown>")
PY
  )"

  echo "About to wipe and rebuild database '${database_name}' configured via .env/AICODING_DATABASE_URL."
  read -r -p "Type RESET to continue: " response
  if [[ "${response}" != "RESET" ]]; then
    echo "Cancelled."
    exit 1
  fi
}

require_confirmation "${1:-}"

run_in_repo_root python3 - <<'PY'
from sqlalchemy.engine import make_url

from aicoding.config import get_settings
from aicoding.db.bootstrap import reset_public_schema
from aicoding.db.session import create_engine_from_settings

settings = get_settings()
engine = create_engine_from_settings()
database_name = make_url(settings.database_url).database or "<unknown>"

try:
    print(f"Resetting database: {database_name}")
    reset_public_schema(engine)
finally:
    engine.dispose()
PY

run_in_repo_root python3 -m aicoding.cli.main admin db ping
run_in_repo_root python3 -m aicoding.cli.main admin db heads
run_in_repo_root python3 -m aicoding.cli.main admin db upgrade
run_in_repo_root python3 -m aicoding.cli.main admin db check-schema
