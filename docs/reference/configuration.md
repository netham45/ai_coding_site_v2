---
doc_type: reference
verified_against:
  - config
config_fields:
  - database_url
  - database_pool_size
  - database_max_overflow
  - database_pool_timeout
  - database_echo
  - daemon_host
  - daemon_port
  - daemon_request_timeout_seconds
  - session_backend
  - session_poll_interval_seconds
  - session_idle_threshold_seconds
  - session_max_nudge_count
  - auth_token
  - auth_token_file
env_vars:
  - AICODING_DATABASE_URL
  - AICODING_DATABASE_POOL_SIZE
  - AICODING_DATABASE_MAX_OVERFLOW
  - AICODING_DATABASE_POOL_TIMEOUT
  - AICODING_DATABASE_ECHO
  - AICODING_DAEMON_HOST
  - AICODING_DAEMON_PORT
  - AICODING_DAEMON_REQUEST_TIMEOUT_SECONDS
  - AICODING_SESSION_BACKEND
  - AICODING_SESSION_POLL_INTERVAL_SECONDS
  - AICODING_SESSION_IDLE_THRESHOLD_SECONDS
  - AICODING_SESSION_MAX_NUDGE_COUNT
  - AICODING_AUTH_TOKEN
  - AICODING_AUTH_TOKEN_FILE
---

# Configuration Reference

The repository loads runtime settings from `.env` using the `AICODING_` prefix.

## Database

- `AICODING_DATABASE_URL`
- `AICODING_DATABASE_POOL_SIZE`
- `AICODING_DATABASE_MAX_OVERFLOW`
- `AICODING_DATABASE_POOL_TIMEOUT`
- `AICODING_DATABASE_ECHO`

## Daemon

- `AICODING_DAEMON_HOST`
- `AICODING_DAEMON_PORT`
- `AICODING_DAEMON_REQUEST_TIMEOUT_SECONDS`

The daemon base URL is derived from host and port.

## Session Runtime

- `AICODING_SESSION_BACKEND`
- `AICODING_SESSION_POLL_INTERVAL_SECONDS`
- `AICODING_SESSION_IDLE_THRESHOLD_SECONDS`
- `AICODING_SESSION_MAX_NUDGE_COUNT`

Current supported backends:

- `tmux`
- `fake`

## Auth

- `AICODING_AUTH_TOKEN`
- `AICODING_AUTH_TOKEN_FILE`

The default token file path is `.runtime/daemon.token`.
